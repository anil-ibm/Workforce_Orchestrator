import json
import smtplib
import sys
import os
import tempfile
from datetime import datetime, UTC
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

# Import BGV verification module
try:
    from bgv_verification import BGVVerificationEngine
    BGV_AVAILABLE = True
except ImportError:
    BGV_AVAILABLE = False
    print("WARNING: BGV verification module not available")

# Import Email notification agent
try:
    from email_notification_agent import EmailNotificationAgent
    EMAIL_AGENT_AVAILABLE = True
except ImportError:
    EMAIL_AGENT_AVAILABLE = False
    print("WARNING: Email notification agent not available")

# Initialize email agent if available
email_agent = None
if EMAIL_AGENT_AVAILABLE:
    email_agent = EmailNotificationAgent()


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "workflow_config.json"
ASSETS_FILE = BASE_DIR / "data" / "assets.json"
EMPLOYEES_FILE = BASE_DIR / "data" / "employees.json"
WORKFLOWS_FILE = BASE_DIR / "data" / "workflows.json"
BGV_RESULTS_FILE = BASE_DIR / "data" / "bgv_verifications.json"
REFERENCE_DOCS_PATH = BASE_DIR / "data"
REALTIME_STAGE_MAP = {
    "onboarding_initiated": {
        "workflow_type": "onboarding",
        "current_stage": "Onboarding Initiated"
    },
    "bgc_completed": {
        "workflow_type": "onboarding",
        "current_stage": "BGC Cleared",
        "default_context": {"bcg_status": "cleared"}
    },
    "assets_initiated": {
        "workflow_type": "onboarding",
        "current_stage": "Assets Initiated"
    },
    "offboarding_completed": {
        "workflow_type": "offboarding",
        "current_stage": "Offboarded"
    }
}


def load_json(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_event_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def now_utc():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def build_email(template, context):
    return {
        "subject": template["subject"].format(**context),
        "body": template["body"].format(**context)
    }


def get_gmail_settings(config):
    provider = config.get("mail_provider", "gmail_smtp")
    if provider != "gmail_smtp":
        raise ValueError(f"Unsupported mail provider: {provider}")

    gmail_config = config.get("gmail_smtp", {})
    required_fields = ["smtp_host", "smtp_port", "sender_email", "sender_password"]
    missing_fields = [field for field in required_fields if not gmail_config.get(field)]
    if missing_fields:
        raise ValueError(f"Missing Gmail SMTP configuration fields: {', '.join(missing_fields)}")
    return gmail_config


def send_mail_via_gmail(notification, gmail_config):
    message = EmailMessage()
    message["From"] = gmail_config["sender_email"]
    message["To"] = notification["to"]
    message["Subject"] = notification["subject"]
    message.set_content(notification["body"])

    with smtplib.SMTP(gmail_config["smtp_host"], gmail_config["smtp_port"], timeout=30) as smtp:
        smtp.ehlo()
        if gmail_config.get("use_tls", True):
            smtp.starttls()
            smtp.ehlo()
        smtp.login(gmail_config["sender_email"], gmail_config["sender_password"])
        smtp.send_message(message)


def send_notifications(notifications, config):
    try:
        # Use the email agent for sending notifications
        print(f"Sending {len(notifications)} email notifications...")
        
        for notification in notifications:
            try:
                # Send email using the email agent
                result = email_agent.send_email(
                    recipient_email=notification["to"],
                    subject=notification["subject"],
                    body_html=notification["body"]
                )
                
                if result['success']:
                    notification["delivery_status"] = "sent"
                    notification["delivery_channel"] = "email_agent_smtp"
                    print(f"✓ Email sent to {notification['to']}: {notification['subject']}")
                else:
                    notification["delivery_status"] = "failed"
                    notification["delivery_channel"] = "email_agent_smtp"
                    notification["error"] = result.get('error', 'Unknown error')
                    print(f"✗ Email failed to {notification['to']}: {result.get('error')}")
                    
            except Exception as e:
                notification["delivery_status"] = "failed"
                notification["delivery_channel"] = "email_agent_smtp"
                notification["error"] = str(e)
                print(f"✗ Email error for {notification['to']}: {str(e)}")
                
    except Exception as e:
        print(f"WARNING: Email delivery system failed: {str(e)}. Continuing workflow without email notifications.")
        for notification in notifications:
            notification["delivery_status"] = "failed"
            notification["delivery_channel"] = "email_agent_smtp"
            notification["error"] = str(e)


def get_employee_record(employees, employee_id):
    return next((employee for employee in employees if employee["employee_id"] == employee_id), None)


def get_asset_rule(config, key, default=False):
    return config.get("asset_rules", {}).get(key, default)


def append_stage(stage_history, stage_name, status, notes):
    stage_history.append({
        "stage": stage_name,
        "status": status,
        "timestamp": now_utc(),
        "notes": notes
    })


def format_asset_summary(items, field_name):
    values = [item.get(field_name) for item in items if item.get(field_name)]
    return ", ".join(values) if values else "none"


def get_stakeholders(event):
    return {
        "employee_email": event["employee_email"],
        "manager_email": event["manager_email"],
        "pmo_email": event["pmo_email"],
        "dsp_reviewer_email": event["dsp_reviewer_email"]
    }


def get_notification_recipients(stage_name, event):
    stakeholders = get_stakeholders(event)
    stage_recipient_map = {
        "screening_approved": [
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "onboarding_initiated": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "bcg_initiated": [
            stakeholders["employee_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "bcg_completed": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "assets_initiated": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "onboarding_completed": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "offboarding_initiated": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ],
        "offboarding_completed": [
            stakeholders["employee_email"],
            stakeholders["manager_email"],
            stakeholders["pmo_email"],
            stakeholders["dsp_reviewer_email"]
        ]
    }
    return stage_recipient_map.get(stage_name, [])


def create_stage_notifications(stage_name, event, config, context):
    notifications = []
    template = config["mail_templates"][stage_name]
    for recipient in get_notification_recipients(stage_name, event):
        notifications.append({
            "to": recipient,
            "stage": stage_name,
            **build_email(template, context)
        })
    return notifications


def create_service_asset(asset_type, employee_id):
    return {
        "asset_id": f"{asset_type.upper()}-{str(uuid4())[:8]}",
        "asset_type": asset_type,
        "model": "Provisioned Service",
        "status": "assigned",
        "assigned_to": employee_id
    }


def assign_assets(requested_assets, employee_id, assets, allow_auto_service_creation=True):
    assigned_assets = []
    pending_assets = []
    initiated_assets = []

    for asset_type in requested_assets:
        initiated_assets.append({
            "asset_type": asset_type,
            "status": "initiated",
            "owner_team": "IT" if asset_type in {"laptop", "mail_id"} else "Admin",
            "initiated_at": now_utc()
        })

        matched_asset = next(
            (
                asset for asset in assets
                if asset["asset_type"] == asset_type and asset["status"] == "available"
            ),
            None
        )

        if matched_asset:
            matched_asset["status"] = "assigned"
            matched_asset["assigned_to"] = employee_id
            assigned_assets.append({
                "asset_id": matched_asset["asset_id"],
                "asset_type": matched_asset["asset_type"],
                "model": matched_asset["model"],
                "status": "assigned",
                "owner_team": "IT" if asset_type in {"laptop", "mail_id"} else "Admin"
            })
            continue

        if allow_auto_service_creation and asset_type in {"mail_id", "welcome_kit"}:
            service_asset = create_service_asset(asset_type, employee_id)
            assets.append(service_asset)
            assigned_assets.append({
                "asset_id": service_asset["asset_id"],
                "asset_type": service_asset["asset_type"],
                "model": service_asset["model"],
                "status": "assigned",
                "owner_team": "IT" if asset_type == "mail_id" else "Admin"
            })
        else:
            pending_assets.append({
                "asset_type": asset_type,
                "status": "pending"
            })

    return assigned_assets, pending_assets, initiated_assets


def release_assets(employee_id, declared_assets, assets):
    returned_assets = []
    missing_assets = []
    revoked_access = []

    for asset_id in declared_assets:
        matched_asset = next((asset for asset in assets if asset["asset_id"] == asset_id), None)
        if matched_asset and matched_asset["assigned_to"] == employee_id:
            matched_asset["status"] = "available"
            matched_asset["assigned_to"] = None
            returned_assets.append(asset_id)
            if matched_asset["asset_type"] == "mail_id":
                revoked_access.append(asset_id)
        else:
            missing_assets.append(asset_id)

    return returned_assets, missing_assets, revoked_access


def update_employee_record_for_onboarding(employees, event, assigned_assets, current_stage):
    employee_record = get_employee_record(employees, event["employee_id"])
    asset_ids = [asset["asset_id"] for asset in assigned_assets]

    if employee_record:
        employee_record.update({
            "employee_name": event["employee_name"],
            "employee_email": event["employee_email"],
            "manager_email": event["manager_email"],
            "pmo_email": event["pmo_email"],
            "dsp_reviewer_email": event["dsp_reviewer_email"],
            "department": event["department"],
            "role": event["role"],
            "project_name": event["project_name"],
            "client_name": event["client_name"],
            "status": "active",
            "current_stage": current_stage,
            "assigned_assets": asset_ids
        })
        return

    employees.append({
        "employee_id": event["employee_id"],
        "employee_name": event["employee_name"],
        "employee_email": event["employee_email"],
        "manager_email": event["manager_email"],
        "pmo_email": event["pmo_email"],
        "dsp_reviewer_email": event["dsp_reviewer_email"],
        "department": event["department"],
        "role": event["role"],
        "project_name": event["project_name"],
        "client_name": event["client_name"],
        "status": "active",
        "current_stage": current_stage,
        "assigned_assets": asset_ids
    })


def update_employee_record_for_offboarding(employees, employee_id, current_stage):
    employee_record = get_employee_record(employees, employee_id)
    if not employee_record:
        return

    employee_record["status"] = "inactive"
    employee_record["assigned_assets"] = []
    employee_record["current_stage"] = current_stage


def create_workflow_record(event, workflow_name, status, current_stage, stage_history, details, notifications):
    return {
        "workflow_id": str(uuid4()),
        "workflow_name": workflow_name,
        "workflow_type": event["workflow_type"],
        "employee_id": event["employee_id"],
        "employee_name": event["employee_name"],
        "status": status,
        "current_stage": current_stage,
        "created_at": now_utc(),
        "stakeholders": get_stakeholders(event),
        "details": details,
        "stage_history": stage_history,
        "notifications": notifications
    }


def build_workflow_context(event, assigned_assets, pending_assets, current_stage, extra_context=None):
    context = {
        "employee_name": event["employee_name"],
        "workflow_type": event["workflow_type"],
        "joining_date": event.get("joining_date", "n/a"),
        "last_working_date": event.get("last_working_date", "n/a"),
        "asset_list": format_asset_summary(assigned_assets, "asset_id") if assigned_assets else "none",
        "asset_types": format_asset_summary(assigned_assets, "asset_type") if assigned_assets else "none",
        "pending_assets": format_asset_summary(pending_assets, "asset_type") if pending_assets else "none",
        "missing_assets": "none",
        "returned_assets": "none",
        "current_stage": current_stage,
        "project_name": event.get("project_name", "n/a"),
        "client_name": event.get("client_name", "n/a"),
        "role": event.get("role", "n/a"),
        "department": event.get("department", "n/a"),
        "bcg_required": "Yes" if event.get("bcg_required") else "No",
        "bcg_status": event.get("bcg_status", "not_required")
    }
    if extra_context:
        context.update(extra_context)
    return context


def process_onboarding(event, config, assets, employees, workflows):
    stage_history = []
    notifications = []

    append_stage(stage_history, "Profile Screening", "completed", "Candidate approved and moved to onboarding queue.")
    screening_context = build_workflow_context(event, [], [], "Profile Screening Approved")
    notifications.extend(create_stage_notifications("screening_approved", event, config, screening_context))

    append_stage(stage_history, "Onboarding Initiated", "completed", "Mandatory onboarding details validated.")
    assigned_assets, pending_assets, initiated_assets = [], [], []
    onboarding_context = build_workflow_context(event, assigned_assets, pending_assets, "Onboarding Initiated")
    notifications.extend(create_stage_notifications("onboarding_initiated", event, config, onboarding_context))
    
    # Send welcome email
    if email_agent:
        try:
            employee_data = {
                "name": event["employee_name"],
                "email": event["employee_email"],
                "employee_id": event.get("employee_id", "TBD"),
                "designation": event.get("role", "N/A"),
                "department": event.get("department", "N/A"),
                "start_date": event.get("joining_date", "TBD")
            }
            email_agent.send_onboarding_welcome_email(employee_data, event.get("manager_email"))
            print(f"[EMAIL] Welcome email sent to {event['employee_email']}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send welcome email: {e}")

    bcg_required = event["bcg_required"]
    bcg_status = "not_required"
    if bcg_required:
        append_stage(stage_history, "BCG", "initiated", "Background check initiated.")
        bcg_status = "initiated"
        bcg_started_context = build_workflow_context(
            event,
            assigned_assets,
            pending_assets,
            "BCG In Progress",
            {"bcg_status": bcg_status}
        )
        notifications.extend(create_stage_notifications("bcg_initiated", event, config, bcg_started_context))
        
        # Send BGC initiation email with portal link
        if email_agent:
            try:
                employee_data = {
                    "name": event["employee_name"],
                    "email": event["employee_email"],
                    "employee_id": event.get("employee_id", "UNKNOWN")
                }
                bgv_portal_url = f"http://127.0.0.1:8053/bgv_portal.html?name={event['employee_name']}&empId={event.get('employee_id', 'UNKNOWN')}&email={event['employee_email']}"
                email_agent.send_bgc_initiation_email(employee_data, bgv_portal_url)
                print(f"[EMAIL] BGC initiation email sent to {event['employee_email']}")
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send BGC email: {e}")

        append_stage(stage_history, "BCG", "completed", "Background check cleared.")
        bcg_status = "cleared"
        event["bcg_status"] = bcg_status
        bcg_completed_context = build_workflow_context(
            event,
            assigned_assets,
            pending_assets,
            "BCG Cleared",
            {"bcg_status": bcg_status}
        )
        notifications.extend(create_stage_notifications("bcg_completed", event, config, bcg_completed_context))
    else:
        append_stage(stage_history, "BCG", "waived", "BCG marked optional for this candidate.")
        event["bcg_status"] = "not_required"

    assigned_assets, pending_assets, initiated_assets = assign_assets(
        event["requested_assets"],
        event["employee_id"],
        assets,
        get_asset_rule(config, "onboarding_auto_create_service_assets", True)
    )
    append_stage(stage_history, "Asset Initiation", "completed", "Asset and access initiation completed.")
    assets_context = build_workflow_context(
        event,
        assigned_assets,
        pending_assets,
        "Assets Initiated",
        {"bcg_status": event["bcg_status"]}
    )
    notifications.extend(create_stage_notifications("assets_initiated", event, config, assets_context))
    
    # Send asset allocation email
    if email_agent and assigned_assets:
        try:
            employee_data = {
                "name": event["employee_name"],
                "email": event["employee_email"],
                "employee_id": event.get("employee_id", "N/A")
            }
            email_agent.send_asset_allocation_email(employee_data, assigned_assets, event.get("manager_email"))
            print(f"[EMAIL] Asset allocation email sent to {event['employee_email']}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send asset allocation email: {e}")

    current_stage = "Onboarded" if not pending_assets else "Asset Initiated with Pending Items"
    append_stage(stage_history, "Onboarding Completed", "completed", "Candidate marked ready for joining or onboarded.")
    completion_context = build_workflow_context(
        event,
        assigned_assets,
        pending_assets,
        current_stage,
        {"bcg_status": event["bcg_status"]}
    )
    notifications.extend(create_stage_notifications("onboarding_completed", event, config, completion_context))

    update_employee_record_for_onboarding(employees, event, assigned_assets, current_stage)

    details = {
        "department": event["department"],
        "role": event["role"],
        "joining_date": event["joining_date"],
        "project_name": event["project_name"],
        "client_name": event["client_name"],
        "screening_status": "Approve",
        "bcg": {
            "required": event["bcg_required"],
            "status": event["bcg_status"],
            "vendor": event.get("bcg_vendor", ""),
            "reference_id": event.get("bcg_reference_id", ""),
            "completed_at": now_utc() if event["bcg_status"] == "cleared" else None
        },
        "assets": {
            "requested_assets": event["requested_assets"],
            "initiated_assets": initiated_assets,
            "assigned_assets": assigned_assets,
            "pending_assets": pending_assets
        }
    }

    status = "completed" if not pending_assets else "completed_with_pending_procurement"
    workflow = create_workflow_record(
        event,
        config["workflow_names"]["onboarding"],
        status,
        current_stage,
        stage_history,
        details,
        notifications
    )
    send_notifications(notifications, config)
    workflows.append(workflow)
    return workflow


def process_offboarding(event, config, assets, employees, workflows):
    stage_history = []
    notifications = []

    append_stage(stage_history, "Offboarding Initiated", "completed", "Employee exit workflow started.")
    started_context = build_workflow_context(event, [], [], "Offboarding Initiated")
    notifications.extend(create_stage_notifications("offboarding_initiated", event, config, started_context))
    
    # Send offboarding initiation email
    if email_agent:
        try:
            employee_data = {
                "name": event["employee_name"],
                "email": event["employee_email"],
                "employee_id": event.get("employee_id", "N/A"),
                "last_working_day": event.get("last_working_date", "TBD")
            }
            email_agent.send_offboarding_initiation_email(employee_data, event.get("manager_email"))
            print(f"[EMAIL] Offboarding initiation email sent to {event['employee_email']}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send offboarding initiation email: {e}")

    returned_assets, missing_assets, revoked_access = release_assets(event["employee_id"], event["assigned_assets"], assets)
    append_stage(stage_history, "Asset Return", "completed", "Assets processed for return or marked missing.")
    append_stage(stage_history, "Access Revocation", "completed", "Logical access reviewed and revoked where applicable.")

    current_stage = "Offboarded" if not missing_assets else "Offboarding Completed with Missing Assets"
    update_employee_record_for_offboarding(employees, event["employee_id"], current_stage)

    completion_context = build_workflow_context(
        event,
        [],
        [],
        current_stage,
        {
            "returned_assets": ", ".join(returned_assets) or "none",
            "missing_assets": ", ".join(missing_assets) or "none"
        }
    )
    notifications.extend(create_stage_notifications("offboarding_completed", event, config, completion_context))
    
    # Send offboarding completion email
    if email_agent:
        try:
            employee_data = {
                "name": event["employee_name"],
                "email": event["employee_email"],
                "employee_id": event.get("employee_id", "N/A")
            }
            email_agent.send_offboarding_completion_email(employee_data, event.get("manager_email"))
            print(f"[EMAIL] Offboarding completion email sent to {event['employee_email']}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send offboarding completion email: {e}")

    details = {
        "last_working_date": event["last_working_date"],
        "returned_assets": returned_assets,
        "missing_assets": missing_assets,
        "revoked_access": revoked_access
    }

    status = "completed" if not missing_assets else "completed_with_missing_assets"
    workflow = create_workflow_record(
        event,
        config["workflow_names"]["offboarding"],
        status,
        current_stage,
        stage_history,
        details,
        notifications
    )
    send_notifications(notifications, config)
    workflows.append(workflow)
    return workflow


def validate_event(event):
    common_fields = [
        "workflow_type",
        "employee_id",
        "employee_name",
        "employee_email",
        "manager_email",
        "pmo_email",
        "dsp_reviewer_email"
    ]
    for field in common_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    if event["workflow_type"] == "onboarding":
        for field in [
            "department",
            "role",
            "joining_date",
            "project_name",
            "client_name",
            "requested_assets",
            "bcg_required"
        ]:
            if field not in event:
                raise ValueError(f"Missing onboarding field: {field}")
        if not isinstance(event["requested_assets"], list) or not event["requested_assets"]:
            raise ValueError("requested_assets must be a non-empty list")
        if not isinstance(event["bcg_required"], bool):
            raise ValueError("bcg_required must be true or false")
    elif event["workflow_type"] == "offboarding":
        for field in ["last_working_date", "assigned_assets"]:
            if field not in event:
                raise ValueError(f"Missing offboarding field: {field}")
        if not isinstance(event["assigned_assets"], list):
            raise ValueError("assigned_assets must be a list")
    else:
        raise ValueError("workflow_type must be 'onboarding' or 'offboarding'")


def validate_realtime_stage_event(payload):
    required_fields = [
        "stage_name",
        "employee_id",
        "employee_name",
        "employee_email",
        "manager_email",
        "pmo_email",
        "dsp_reviewer_email"
    ]
    for field in required_fields:
        if not payload.get(field):
            raise ValueError(f"Missing realtime field: {field}")

    stage_name = payload["stage_name"]
    if stage_name not in REALTIME_STAGE_MAP:
        raise ValueError(
            "stage_name must be one of: "
            + ", ".join(sorted(REALTIME_STAGE_MAP.keys()))
        )


def create_realtime_workflow_record(stage_name, event, notifications, current_stage):
    return {
        "workflow_id": str(uuid4()),
        "workflow_name": f"Realtime Stage Trigger - {stage_name}",
        "workflow_type": event["workflow_type"],
        "employee_id": event["employee_id"],
        "employee_name": event["employee_name"],
        "status": "notification_sent",
        "current_stage": current_stage,
        "created_at": now_utc(),
        "stakeholders": get_stakeholders(event),
        "details": {
            "trigger_mode": "realtime_api",
            "stage_name": stage_name
        },
        "stage_history": [
            {
                "stage": current_stage,
                "status": "completed",
                "timestamp": now_utc(),
                "notes": f"Realtime notification triggered for {stage_name}."
            }
        ],
        "notifications": notifications
    }


def trigger_realtime_stage_event(payload):
    validate_realtime_stage_event(payload)
    config = load_json(CONFIG_FILE)
    workflows = load_json(WORKFLOWS_FILE)

    stage_name = payload["stage_name"]
    stage_config = REALTIME_STAGE_MAP[stage_name]
    event = {
        "workflow_type": stage_config["workflow_type"],
        "employee_id": payload["employee_id"],
        "employee_name": payload["employee_name"],
        "employee_email": payload["employee_email"],
        "manager_email": payload["manager_email"],
        "pmo_email": payload["pmo_email"],
        "dsp_reviewer_email": payload["dsp_reviewer_email"],
        "joining_date": payload.get("joining_date", "n/a"),
        "last_working_date": payload.get("last_working_date", "n/a"),
        "project_name": payload.get("project_name", "n/a"),
        "client_name": payload.get("client_name", "n/a"),
        "role": payload.get("role", "n/a"),
        "department": payload.get("department", "n/a"),
        "bcg_required": payload.get("bcg_required", False),
        "bcg_status": payload.get("bcg_status", "not_required")
    }

    extra_context = stage_config.get("default_context", {}).copy()
    extra_context.update(payload.get("context", {}))
    context = build_workflow_context(
        event,
        payload.get("assigned_assets", []),
        payload.get("pending_assets", []),
        stage_config["current_stage"],
        extra_context
    )
    notifications = create_stage_notifications(stage_name, event, config, context)
    send_notifications(notifications, config)

    workflow = create_realtime_workflow_record(
        stage_name,
        event,
        notifications,
        stage_config["current_stage"]
    )
    workflows.append(workflow)
    save_json(WORKFLOWS_FILE, workflows)
    return workflow


def summarize_dashboard_candidates(candidates):
    approved = []
    nominated = []
    rejected = []
    on_hold = []

    for candidate in candidates:
        status = str(candidate.get("status", "")).strip().lower()
        if "approve" in status or "onboard" in status:
            approved.append(candidate)
        elif "nominated" in status:
            nominated.append(candidate)
        elif "reject" in status:
            rejected.append(candidate)
        elif "hold" in status:
            on_hold.append(candidate)

    return {
        "total": len(candidates),
        "approved": approved,
        "nominated": nominated,
        "rejected": rejected,
        "hold": on_hold
    }


def build_assistant_reply(payload):
    query = str(payload.get("query", "")).strip()
    normalized_query = query.lower()
    context = payload.get("dashboard_context", {}) or {}
    candidates = payload.get("candidates", []) or []
    summary = summarize_dashboard_candidates(candidates)

    active_section = context.get("activeSection", "homeSection")
    active_candidate = context.get("activeCandidateName", "")
    workflow_stage = context.get("workflowStage", "")
    visible_candidate_count = context.get("visibleCandidateCount", len(candidates))
    screening_status_filter = context.get("screeningStatusFilter", "")
    screening_experience_filter = context.get("screeningExperienceFilter", "")
    onboarding_status_filter = context.get("onboardingStatusFilter", "")

    if not query:
        return (
            "Ask about onboarding, offboarding, candidate status, asset tracking, BGC, email triggers, "
            "workflow progress, or dashboard issues."
        )

    if "how many" in normalized_query or "count" in normalized_query or "total" in normalized_query:
        return (
            f"There are {summary['total']} candidates available in the current Workforce Orchestrator context. "
            f"Approved/onboarded: {len(summary['approved'])}, nominated: {len(summary['nominated'])}, "
            f"hold: {len(summary['hold'])}, rejected: {len(summary['rejected'])}. "
            f"Visible candidates in the current dashboard view: {visible_candidate_count}."
        )

    if "approved" in normalized_query or "onboarded" in normalized_query:
        names = ", ".join(candidate.get("name", "Unknown") for candidate in summary["approved"][:10]) or "none"
        return (
            f"Approved or onboarded candidates: {len(summary['approved'])}. "
            f"Sample candidates: {names}. "
            f"Current onboarding status filter: {onboarding_status_filter or 'not applied'}."
        )

    if "nominated" in normalized_query:
        names = ", ".join(candidate.get("name", "Unknown") for candidate in summary["nominated"][:10]) or "none"
        return (
            f"Nominated candidates: {len(summary['nominated'])}. "
            f"Sample candidates: {names}. "
            f"Current screening status filter: {screening_status_filter or 'not applied'}."
        )

    if "reject" in normalized_query:
        names = ", ".join(candidate.get("name", "Unknown") for candidate in summary["rejected"][:10]) or "none"
        return f"Rejected candidates: {len(summary['rejected'])}. Sample candidates: {names}."

    if "hold" in normalized_query:
        names = ", ".join(candidate.get("name", "Unknown") for candidate in summary["hold"][:10]) or "none"
        return f"Candidates on hold: {len(summary['hold'])}. Sample candidates: {names}."

    if "experience" in normalized_query or "years" in normalized_query:
        return (
            f"Current experience filter in Profile Screening is "
            f"{screening_experience_filter or 'not applied'}. "
            "Use prompts like 'show candidates with 5+ years' to refine candidate views."
        )

    if "asset" in normalized_query:
        return (
            "Asset tracking is managed in the workflow view. "
            "You can track initiation, assignment, pending items, and offboarding recovery. "
            f"Current active candidate: {active_candidate or 'not selected'}."
        )

    if "bgc" in normalized_query or "background" in normalized_query:
        return (
            "BGC is tracked as a workflow stage after onboarding initiation. "
            "When BGC completes, realtime email notifications can be triggered from the dashboard workflow actions."
        )

    if "mail" in normalized_query or "email" in normalized_query or "trigger" in normalized_query:
        return (
            "Realtime email triggers are configured for onboarding, BGC completion, asset initiation, and offboarding. "
            "If mails are not sent, verify Gmail SMTP settings in workflow_config.json and confirm the realtime API is running on port 8050."
        )

    if "issue" in normalized_query or "problem" in normalized_query or "error" in normalized_query or "dashboard" in normalized_query:
        return (
            f"Current dashboard context: section={active_section}, active candidate={active_candidate or 'none'}, "
            f"workflow stage={workflow_stage or 'not set'}, visible candidates={visible_candidate_count}. "
            "If something is not working, verify the selected section, candidate data, browser console errors, and realtime API availability."
        )

    if "workflow" in normalized_query or "stage" in normalized_query or "progress" in normalized_query:
        return (
            f"Current workflow context: section={active_section}, "
            f"active candidate={active_candidate or 'none'}, stage={workflow_stage or 'not set'}. "
            "Typical lifecycle is Profile Screening -> Onboarding -> BGC -> Asset Initiated -> Offboarded, depending on the case."
        )

    if "candidate" in normalized_query or "list" in normalized_query or "who" in normalized_query:
        names = ", ".join(candidate.get("name", "Unknown") for candidate in candidates[:12]) or "none"
        return f"Candidates in the current Workforce Orchestrator context: {names}."

    return (
        "I can help with dashboard issues, onboarding, offboarding, candidate status, BGC, asset tracking, "
        "email trigger troubleshooting, and workflow progress inside Workforce Orchestrator."
    )


def handle_bgv_verification(uploaded_files, employee_info):
    """Handle BGV document verification"""
    if not BGV_AVAILABLE:
        return {
            "error": "BGV verification module not available",
            "verification_status": "error"
        }
    
    try:
        # Get Gemini API key from environment or config
        config = load_json(CONFIG_FILE)
        # Handle both dict and list returns from load_json
        if isinstance(config, dict):
            gemini_api_key = os.environ.get('GEMINI_API_KEY') or config.get('gemini_api_key')
        else:
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
        
        if not gemini_api_key:
            return {
                "error": "Gemini API key not configured. Set GEMINI_API_KEY environment variable or add to config.",
                "verification_status": "error"
            }
        
        # Initialize BGV engine
        bgv_engine = BGVVerificationEngine(gemini_api_key, REFERENCE_DOCS_PATH)
        
        # Save uploaded files temporarily
        temp_dir = Path(tempfile.gettempdir()) / "bgv_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        aadhaar_front_path = temp_dir / f"aadhaar_front_{employee_info['employee_id']}.jpg"
        aadhaar_back_path = temp_dir / f"aadhaar_back_{employee_info['employee_id']}.jpg"
        details_form_path = temp_dir / f"details_form_{employee_info['employee_id']}.pdf"
        resume_path = temp_dir / f"resume_{employee_info['employee_id']}.pdf"
        
        # Write files
        with open(aadhaar_front_path, 'wb') as f:
            f.write(uploaded_files['aadhaar_front'])
        with open(aadhaar_back_path, 'wb') as f:
            f.write(uploaded_files['aadhaar_back'])
        with open(details_form_path, 'wb') as f:
            f.write(uploaded_files['details_form'])
        with open(resume_path, 'wb') as f:
            f.write(uploaded_files['resume'])
        
        # Perform verification
        verification_result = bgv_engine.verify_documents(
            aadhaar_front_path,
            aadhaar_back_path,
            details_form_path,
            employee_info,
            resume_path
        )
        
        # Save verification results
        bgv_results = load_json(BGV_RESULTS_FILE)
        bgv_results.append(verification_result)
        save_json(BGV_RESULTS_FILE, bgv_results)
        
        # Update workflow if BGV is approved
        if verification_result['verification_status'] == 'approved':
            workflows = load_json(WORKFLOWS_FILE)
            # Find the employee's onboarding workflow
            for workflow in workflows:
                if (workflow.get('employee_id') == employee_info['employee_id'] and
                    workflow.get('workflow_type') == 'onboarding'):
                    workflow['bgv_verification_id'] = verification_result['verification_id']
                    workflow['bgv_status'] = 'verified'
                    workflow['bgv_verified_at'] = verification_result['timestamp']
                    break
            save_json(WORKFLOWS_FILE, workflows)
        
        # Send BGC completion email
        if email_agent:
            try:
                employee_data = {
                    "name": employee_info['employee_name'],
                    "email": employee_info['employee_email'],
                    "employee_id": employee_info['employee_id']
                }
                # Map verification_status to email status
                email_status = verification_result['verification_status']
                if email_status == 'approved':
                    email_status = 'successful'
                
                # Get manager email from workflows
                manager_email = None
                workflows = load_json(WORKFLOWS_FILE)
                for workflow in workflows:
                    if workflow.get('employee_id') == employee_info['employee_id']:
                        manager_email = workflow.get('stakeholders', {}).get('manager_email')
                        break
                
                email_agent.send_bgc_completion_email(employee_data, email_status, manager_email)
                print(f"[EMAIL] BGC completion email sent to {employee_info['employee_email']}")
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send BGC completion email: {e}")
        
        # Clean up temp files
        try:
            aadhaar_front_path.unlink()
            aadhaar_back_path.unlink()
            details_form_path.unlink()
            resume_path.unlink()
        except:
            pass
        
        return verification_result
        
    except Exception as e:
        return {
            "error": str(e),
            "verification_status": "error"
        }


class RealtimeWorkflowRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    
    def do_GET(self):
        """Handle GET requests for serving HTML files and data files"""
        try:
            # Parse path without query parameters
            path = self.path.split('?')[0]
            
            # Determine file path and content type
            if path == "/" or path == "/dashboard.html":
                file_path = Path("dashboard.html")
                content_type = "text/html; charset=utf-8"
            elif path == "/bgv_portal.html":
                file_path = Path("bgv_portal.html")
                content_type = "text/html; charset=utf-8"
            elif path == "/screening_records.js":
                file_path = Path("screening_records.js")
                content_type = "application/javascript; charset=utf-8"
            elif path.startswith("/data/"):
                # Serve data files (CSV, JSON, etc.)
                file_path = Path(path[1:])  # Remove leading slash
                if path.endswith('.csv'):
                    content_type = "text/csv; charset=utf-8"
                elif path.endswith('.json'):
                    content_type = "application/json; charset=utf-8"
                else:
                    content_type = "text/plain; charset=utf-8"
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>404 - Not Found</h1>")
                return
            
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h1>404 - File not found: {file_path}</h1>".encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h1>500 - Server Error: {str(e)}</h1>".encode())
    
    def do_OPTIONS(self):
        self._send_json(200, {"status": "ok"})
    
    def parse_multipart(self):
        """Parse multipart form data for file uploads"""
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            return None, None
        
        try:
            # Parse boundary - handle it as bytes from the start
            boundary_str = content_type.split('boundary=')[1]
            # Remove any quotes if present
            boundary_str = boundary_str.strip('"')
            boundary = boundary_str.encode('latin-1')
            
            # Read the body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse multipart data
            files = {}
            fields = {}
            
            parts = body.split(b'--' + boundary)
            for part in parts:
                if b'Content-Disposition' not in part:
                    continue
                
                # Extract headers and content - be more careful with encoding
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    header_end = part.find(b'\n\n')
                    if header_end == -1:
                        continue
                    header_bytes = part[:header_end]
                    content = part[header_end+2:].rstrip(b'\r\n')
                else:
                    header_bytes = part[:header_end]
                    content = part[header_end+4:].rstrip(b'\r\n')
                
                # Try to decode headers as ASCII/Latin-1 (safer for HTTP headers)
                try:
                    headers = header_bytes.decode('latin-1')
                except:
                    headers = header_bytes.decode('utf-8', errors='replace')
                
                # Extract field name
                if 'name="' in headers:
                    name_start = headers.find('name="') + 6
                    name_end = headers.find('"', name_start)
                    field_name = headers[name_start:name_end]
                    
                    # Check if it's a file
                    if 'filename="' in headers:
                        # Store file content as-is (binary)
                        files[field_name] = content
                    else:
                        # Try to decode text fields
                        try:
                            fields[field_name] = content.decode('utf-8')
                        except:
                            fields[field_name] = content.decode('latin-1', errors='replace')
            
            return files, fields
            
        except Exception as e:
            print(f"Error parsing multipart data: {e}")
            return None, None

    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        
        try:
            # Handle multipart form data (file uploads)
            if content_type.startswith('multipart/form-data'):
                files, fields = self.parse_multipart()
                
                if self.path == "/api/bgv-verify":
                    if not files or not all(k in files for k in ['aadhaar_front', 'aadhaar_back', 'details_form', 'resume']):
                        missing = [k for k in ['aadhaar_front', 'aadhaar_back', 'details_form', 'resume'] if k not in (files or {})]
                        self._send_json(400, {"error": f"Missing required files: {', '.join(missing)}"})
                        return
                    
                    if fields is None:
                        fields = {}
                    
                    employee_info = {
                        "employee_id": fields.get('employee_id', 'UNKNOWN') if fields else 'UNKNOWN',
                        "employee_name": fields.get('employee_name', 'UNKNOWN') if fields else 'UNKNOWN',
                        "employee_email": fields.get('employee_email', 'UNKNOWN') if fields else 'UNKNOWN'
                    }
                    
                    result = handle_bgv_verification(files, employee_info)
                    
                    if result.get('verification_status') == 'error':
                        self._send_json(500, result)
                    else:
                        self._send_json(200, result)
                    return
            
            # Handle JSON requests
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(raw_body.decode("utf-8"))

            if self.path == "/api/realtime-stage-trigger":
                workflow = trigger_realtime_stage_event(payload)
                self._send_json(200, {
                    "message": "Realtime stage notification sent",
                    "workflow_id": workflow["workflow_id"],
                    "current_stage": workflow["current_stage"],
                    "notifications_generated": len(workflow["notifications"])
                })
                return

            if self.path == "/api/chatbot":
                reply = build_assistant_reply(payload)
                self._send_json(200, {"reply": reply})
                return

            if self.path == "/api/refresh-candidates":
                # Run the generate_candidates_from_resumes.py script
                try:
                    import subprocess
                    result = subprocess.run(
                        [sys.executable, "scripts/generate_candidates_from_resumes.py"],
                        capture_output=True,
                        text=True,
                        cwd=Path.cwd()
                    )
                    
                    if result.returncode == 0:
                        # Count candidates in the generated file
                        try:
                            with open("screening_records.js", "r", encoding="utf-8") as f:
                                content = f.read()
                                # Count candidate objects
                                count = content.count("candidateName:")
                            
                            self._send_json(200, {
                                "status": "success",
                                "message": "Candidates refreshed successfully",
                                "count": count,
                                "output": result.stdout
                            })
                        except Exception as e:
                            self._send_json(200, {
                                "status": "success",
                                "message": "Candidates refreshed successfully",
                                "output": result.stdout
                            })
                    else:
                        self._send_json(500, {
                            "status": "error",
                            "message": "Failed to refresh candidates",
                            "error": result.stderr
                        })
                except Exception as e:
                    self._send_json(500, {
                        "status": "error",
                        "message": f"Error running refresh script: {str(e)}"
                    })
                return

            self._send_json(404, {"error": "Not found"})
        except Exception as error:
            self._send_json(400, {"error": str(error)})


def run_realtime_api_server(host="127.0.0.1", port=8050):
    server = ThreadingHTTPServer((host, port), RealtimeWorkflowRequestHandler)
    print(f"Realtime Workflow API running on http://{host}:{port}")
    server.serve_forever()


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--serve-api":
        port = int(sys.argv[2]) if len(sys.argv) >= 3 else 8050
        run_realtime_api_server(port=port)
        return

    if len(sys.argv) != 2:
        print("Usage: python scripts/workforce_orchestrator.py <event_json_file>")
        print("   or: python scripts/workforce_orchestrator.py --serve-api [port]")
        sys.exit(1)

    event_file = Path(sys.argv[1]).resolve()
    event = load_event_json(event_file)
    validate_event(event)

    config = load_json(CONFIG_FILE)
    assets = load_json(ASSETS_FILE)
    employees = load_json(EMPLOYEES_FILE)
    workflows = load_json(WORKFLOWS_FILE)

    if event["workflow_type"] == "onboarding":
        workflow = process_onboarding(event, config, assets, employees, workflows)
    else:
        workflow = process_offboarding(event, config, assets, employees, workflows)

    save_json(ASSETS_FILE, assets)
    save_json(EMPLOYEES_FILE, employees)
    save_json(WORKFLOWS_FILE, workflows)

    print(json.dumps({
        "workflow_id": workflow["workflow_id"],
        "workflow_type": workflow["workflow_type"],
        "status": workflow["status"],
        "current_stage": workflow["current_stage"],
        "employee_id": workflow["employee_id"],
        "notifications_generated": len(workflow["notifications"])
    }, indent=2))


if __name__ == "__main__":
    main()

# Made with Bob
