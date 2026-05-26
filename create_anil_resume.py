"""
Script to create Anil Kumar M's resume in PDF format
Run this script to generate the PDF resume
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib.colors import HexColor
    print("✓ reportlab library found")
except ImportError:
    print("ERROR: reportlab library not installed")
    print("Please install it using: pip install reportlab")
    exit(1)

def create_resume():
    """Create Anil Kumar M's resume PDF"""
    
    # Create PDF
    filename = "Resumes/Anil_Kumar_M_Data_Engineer_Resume.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#666666'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=HexColor('#667eea'),
        borderPadding=5,
        backColor=HexColor('#f0f0f0')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        spaceAfter=4,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    # Header
    elements.append(Paragraph("ANIL KUMAR M", title_style))
    elements.append(Paragraph("Data Engineer", subtitle_style))
    elements.append(Paragraph(
        "Email: manilkumar1909@gmail.com | Phone: +91-9876543210 | Location: Bangalore, India",
        contact_style
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    # Professional Summary
    elements.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    elements.append(Paragraph(
        "Results-driven Data Engineer with 5+ years of experience in designing, developing, and maintaining "
        "scalable data pipelines and ETL processes. Expertise in big data technologies, cloud platforms (AWS, Azure), "
        "and data warehousing solutions. Proven track record of optimizing data infrastructure and implementing "
        "robust data solutions that drive business insights.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # Technical Skills
    elements.append(Paragraph("TECHNICAL SKILLS", heading_style))
    skills = [
        "<b>Programming:</b> Python, SQL, Scala, Java, Shell Scripting",
        "<b>Big Data:</b> Apache Spark, Kafka, Airflow, Hadoop, Hive, HBase",
        "<b>Cloud:</b> AWS (S3, EMR, Glue, Redshift, Lambda), Azure (Data Factory, Databricks, Synapse)",
        "<b>Databases:</b> PostgreSQL, MySQL, MongoDB, Cassandra, Redis, Snowflake",
        "<b>Tools:</b> Docker, Kubernetes, Git, Jenkins, dbt, Great Expectations",
        "<b>Visualization:</b> Tableau, Power BI, Looker, Grafana"
    ]
    for skill in skills:
        elements.append(Paragraph(f"• {skill}", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Professional Experience
    elements.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
    
    # Job 1
    elements.append(Paragraph("<b>Senior Data Engineer</b> | Tech Solutions Pvt Ltd, Bangalore", body_style))
    elements.append(Paragraph("<i>June 2021 - Present (3 years)</i>", body_style))
    job1_points = [
        "Designed and implemented end-to-end data pipelines processing 10TB+ daily data using Apache Spark and AWS EMR, reducing processing time by 40%",
        "Built real-time streaming data pipelines using Apache Kafka and Spark Streaming to process 1M+ events per second",
        "Migrated legacy ETL processes to cloud-native solutions on AWS, resulting in 60% cost reduction",
        "Implemented data quality frameworks using Great Expectations, reducing data quality issues by 75%",
        "Led a team of 3 junior data engineers, providing mentorship and code reviews"
    ]
    for point in job1_points:
        elements.append(Paragraph(f"• {point}", bullet_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Job 2
    elements.append(Paragraph("<b>Data Engineer</b> | DataTech Solutions, Hyderabad", body_style))
    elements.append(Paragraph("<i>March 2020 - May 2021 (1 year 3 months)</i>", body_style))
    job2_points = [
        "Developed and maintained 50+ ETL pipelines using Apache Airflow and Python",
        "Implemented data warehouse solution on Snowflake, consolidating data from 10+ operational systems",
        "Created automated data validation and monitoring systems, reducing manual effort by 80%",
        "Collaborated with data scientists to build feature engineering pipelines for ML models"
    ]
    for point in job2_points:
        elements.append(Paragraph(f"• {point}", bullet_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Job 3
    elements.append(Paragraph("<b>Junior Data Engineer</b> | InfoSys Technologies, Bangalore", body_style))
    elements.append(Paragraph("<i>January 2019 - February 2020 (1 year 2 months)</i>", body_style))
    job3_points = [
        "Developed ETL scripts using Python and SQL to extract, transform, and load data into data warehouse",
        "Assisted in designing and implementing data models for reporting and analytics",
        "Created automated reports and dashboards using Tableau and Power BI",
        "Performed data quality checks and data profiling on source systems"
    ]
    for point in job3_points:
        elements.append(Paragraph(f"• {point}", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Key Projects
    elements.append(Paragraph("KEY PROJECTS", heading_style))
    projects = [
        "<b>Real-Time Fraud Detection System:</b> Built real-time fraud detection pipeline using Kafka and Spark Streaming, processing 1M+ transactions/day with 95% accuracy",
        "<b>Data Lake Implementation:</b> Designed enterprise data lake on AWS, ingesting data from 20+ sources with automated cataloging",
        "<b>Customer Data Platform:</b> Built unified customer view integrating 15+ data sources, reducing data retrieval time by 70%",
        "<b>ML Feature Store:</b> Developed centralized feature store using Databricks and Delta Lake, reducing model development time by 50%"
    ]
    for project in projects:
        elements.append(Paragraph(f"• {project}", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Education
    elements.append(Paragraph("EDUCATION", heading_style))
    elements.append(Paragraph(
        "<b>Bachelor of Technology (B.Tech) in Computer Science Engineering</b>",
        body_style
    ))
    elements.append(Paragraph(
        "Visvesvaraya Technological University, Karnataka | 2014 - 2018 | CGPA: 8.5/10",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # Certifications
    elements.append(Paragraph("CERTIFICATIONS", heading_style))
    certs = [
        "AWS Certified Data Analytics - Specialty (2023)",
        "Azure Data Engineer Associate (DP-203) (2022)",
        "Databricks Certified Associate Developer for Apache Spark (2021)",
        "Google Cloud Professional Data Engineer (2022)"
    ]
    for cert in certs:
        elements.append(Paragraph(f"• {cert}", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Achievements
    elements.append(Paragraph("KEY ACHIEVEMENTS", heading_style))
    achievements = [
        "Reduced data pipeline execution time by 40% through optimization techniques",
        "Implemented cost optimization strategies saving $50K annually in cloud costs",
        "Successfully migrated 200+ ETL jobs from on-premise to cloud with zero downtime",
        "Received 'Outstanding Performer' award for Q3 2023"
    ]
    for achievement in achievements:
        elements.append(Paragraph(f"• {achievement}", bullet_style))
    
    # Build PDF
    doc.build(elements)
    print(f"\n✓ Resume PDF created successfully: {filename}")
    print(f"✓ File location: {filename}")
    print("\nResume Details:")
    print(f"  Name: Anil Kumar M")
    print(f"  Email: manilkumar1909@gmail.com")
    print(f"  Role: Data Engineer")
    print(f"  Experience: 5 years")

if __name__ == "__main__":
    print("Creating Anil Kumar M's resume PDF...")
    print("-" * 50)
    try:
        create_resume()
        print("-" * 50)
        print("SUCCESS! Resume is ready for BGV verification.")
    except Exception as e:
        print(f"\nERROR: Failed to create PDF")
        print(f"Error details: {str(e)}")
        print("\nPlease ensure:")
        print("1. reportlab is installed: pip install reportlab")
        print("2. Resumes folder exists")
        print("3. You have write permissions")

# Made with Bob
