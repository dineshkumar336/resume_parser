"""
Script to generate the synthetic jobs dataset for the Resume Builder.
Run this once to create data/jobs_dataset.csv
"""
import csv
import os
import random

JOBS = [
    # Software Engineering
    {"job_title": "Junior Software Engineer", "company": "TechNova Inc.", "location": "Bangalore, India", "category": "Software Engineering", "experience_level": "Entry Level", "salary_range": "4-8 LPA",
     "required_skills": "python, java, git, sql, data structures, algorithms, problem solving, rest api",
     "description": "We are looking for a Junior Software Engineer to join our development team. You will work on building and maintaining web applications, writing clean code, debugging software, and collaborating with senior developers. Knowledge of data structures, algorithms, and version control is essential."},
    {"job_title": "Software Developer", "company": "Infosys", "location": "Hyderabad, India", "category": "Software Engineering", "experience_level": "Entry Level", "salary_range": "3.5-7 LPA",
     "required_skills": "java, spring boot, mysql, git, agile, rest api, junit, problem solving",
     "description": "Join Infosys as a Software Developer working on enterprise Java applications. You will design, develop and test software modules using Spring Boot and MySQL. Experience with agile methodologies and writing unit tests is preferred."},
    {"job_title": "Backend Developer", "company": "Flipkart", "location": "Bangalore, India", "category": "Software Engineering", "experience_level": "Mid Level", "salary_range": "12-22 LPA",
     "required_skills": "java, python, microservices, docker, kubernetes, redis, mongodb, kafka, system design",
     "description": "Flipkart is hiring a Backend Developer to build scalable microservices handling millions of requests. You will work on distributed systems, optimize database queries, and implement event-driven architectures using Kafka."},
    {"job_title": "Senior Software Engineer", "company": "Google", "location": "Bangalore, India", "category": "Software Engineering", "experience_level": "Senior Level", "salary_range": "35-60 LPA",
     "required_skills": "c++, python, distributed systems, system design, algorithms, leadership, mentoring, ci/cd",
     "description": "Google is looking for a Senior Software Engineer to lead the development of large-scale distributed systems. You will mentor junior engineers, drive technical decisions, and build infrastructure used by billions of users worldwide."},
    {"job_title": "Full Stack Developer", "company": "Zoho", "location": "Chennai, India", "category": "Software Engineering", "experience_level": "Mid Level", "salary_range": "8-15 LPA",
     "required_skills": "javascript, react, node.js, express, mongodb, html, css, git, rest api, agile",
     "description": "Zoho seeks a Full Stack Developer proficient in React and Node.js to build end-to-end features for our SaaS products. You will collaborate with designers and product managers to deliver polished user experiences."},

    # Data Science & Analytics
    {"job_title": "Data Analyst", "company": "Deloitte", "location": "Mumbai, India", "category": "Data Science", "experience_level": "Entry Level", "salary_range": "4-8 LPA",
     "required_skills": "python, sql, excel, tableau, pandas, numpy, statistics, communication, analytical thinking",
     "description": "Deloitte is hiring a Data Analyst to transform raw data into actionable business insights. You will create dashboards in Tableau, write SQL queries to extract data, and present findings to stakeholders."},
    {"job_title": "Data Scientist", "company": "Amazon", "location": "Hyderabad, India", "category": "Data Science", "experience_level": "Mid Level", "salary_range": "18-35 LPA",
     "required_skills": "python, machine learning, tensorflow, pandas, numpy, scikit-learn, sql, statistics, deep learning, nlp",
     "description": "Amazon is looking for a Data Scientist to build ML models that improve customer experience. You will work on recommendation engines, demand forecasting, and NLP-based solutions using TensorFlow and scikit-learn."},
    {"job_title": "ML Engineer", "company": "Microsoft", "location": "Noida, India", "category": "Data Science", "experience_level": "Mid Level", "salary_range": "20-40 LPA",
     "required_skills": "python, pytorch, tensorflow, mlflow, docker, kubernetes, ci/cd, deep learning, computer vision",
     "description": "Microsoft seeks an ML Engineer to productionize machine learning models. You will build ML pipelines, optimize model performance, and deploy models at scale using MLOps best practices."},
    {"job_title": "Business Intelligence Analyst", "company": "Accenture", "location": "Pune, India", "category": "Data Science", "experience_level": "Entry Level", "salary_range": "5-9 LPA",
     "required_skills": "sql, power bi, excel, python, statistics, data visualization, communication, analytical thinking",
     "description": "Accenture is hiring a BI Analyst to design interactive Power BI dashboards and automate reporting. You will analyze business data, identify trends, and support data-driven decision making across teams."},
    {"job_title": "AI Research Scientist", "company": "DeepMind", "location": "Remote", "category": "Data Science", "experience_level": "Senior Level", "salary_range": "50-90 LPA",
     "required_skills": "python, pytorch, deep learning, reinforcement learning, mathematics, research, nlp, computer vision, publications",
     "description": "DeepMind is seeking an AI Research Scientist to push the boundaries of artificial intelligence. You will publish papers at top conferences, develop novel architectures, and contribute to foundational AI research."},

    # Web Development
    {"job_title": "Frontend Developer", "company": "Swiggy", "location": "Bangalore, India", "category": "Web Development", "experience_level": "Entry Level", "salary_range": "5-10 LPA",
     "required_skills": "html, css, javascript, react, git, responsive design, figma, rest api, problem solving",
     "description": "Swiggy is looking for a Frontend Developer to build beautiful, responsive web interfaces using React. You will work closely with designers to translate Figma mockups into pixel-perfect, performant UIs."},
    {"job_title": "React Developer", "company": "Razorpay", "location": "Bangalore, India", "category": "Web Development", "experience_level": "Mid Level", "salary_range": "12-20 LPA",
     "required_skills": "react, typescript, next.js, css, tailwind, jest, git, ci/cd, performance optimization",
     "description": "Razorpay seeks an experienced React Developer to build and maintain our payment dashboard. You will optimize performance, write comprehensive tests, and implement complex financial UI components."},
    {"job_title": "WordPress Developer", "company": "WebCraft Solutions", "location": "Delhi, India", "category": "Web Development", "experience_level": "Entry Level", "salary_range": "3-6 LPA",
     "required_skills": "html, css, javascript, php, wordpress, mysql, seo, responsive design",
     "description": "WebCraft Solutions is hiring a WordPress Developer to build and customize WordPress themes and plugins. You will work on client websites, ensure SEO optimization, and maintain existing sites."},
    {"job_title": "UI/UX Designer", "company": "Ola", "location": "Bangalore, India", "category": "Web Development", "experience_level": "Mid Level", "salary_range": "10-18 LPA",
     "required_skills": "figma, adobe xd, sketch, user research, wireframing, prototyping, design thinking, communication",
     "description": "Ola is looking for a UI/UX Designer to create intuitive and delightful user experiences for our ride-hailing platform. You will conduct user research, create wireframes and prototypes, and collaborate with engineering teams."},
    {"job_title": "Angular Developer", "company": "TCS", "location": "Pune, India", "category": "Web Development", "experience_level": "Entry Level", "salary_range": "4-7 LPA",
     "required_skills": "angular, typescript, html, css, javascript, rxjs, git, rest api, agile",
     "description": "TCS is hiring an Angular Developer for enterprise web applications. You will build dynamic single-page apps using Angular, integrate with REST APIs, and follow agile development practices."},

    # DevOps & Cloud
    {"job_title": "DevOps Engineer", "company": "Hashedin", "location": "Bangalore, India", "category": "DevOps", "experience_level": "Mid Level", "salary_range": "10-20 LPA",
     "required_skills": "docker, kubernetes, aws, terraform, jenkins, linux, python, ci/cd, monitoring, ansible",
     "description": "Hashedin seeks a DevOps Engineer to automate infrastructure provisioning and manage CI/CD pipelines. You will work with Docker, Kubernetes, and Terraform on AWS to ensure high availability and scalability."},
    {"job_title": "Cloud Architect", "company": "Wipro", "location": "Hyderabad, India", "category": "DevOps", "experience_level": "Senior Level", "salary_range": "25-45 LPA",
     "required_skills": "aws, azure, google cloud, terraform, kubernetes, microservices, system design, security, leadership",
     "description": "Wipro is looking for a Cloud Architect to design and implement cloud-native solutions for enterprise clients. You will lead cloud migration projects, define architecture standards, and mentor cloud engineering teams."},
    {"job_title": "Site Reliability Engineer", "company": "PhonePe", "location": "Bangalore, India", "category": "DevOps", "experience_level": "Mid Level", "salary_range": "15-28 LPA",
     "required_skills": "linux, python, kubernetes, prometheus, grafana, docker, terraform, incident management, automation",
     "description": "PhonePe is hiring an SRE to ensure our payment platform maintains 99.99% uptime. You will build monitoring systems, automate incident response, and optimize infrastructure performance."},
    {"job_title": "AWS Solutions Architect", "company": "Cognizant", "location": "Chennai, India", "category": "DevOps", "experience_level": "Mid Level", "salary_range": "12-22 LPA",
     "required_skills": "aws, ec2, s3, lambda, cloudformation, vpc, iam, rds, dynamodb, aws certified",
     "description": "Cognizant seeks an AWS Solutions Architect to design cloud architectures for clients. You will conduct cloud readiness assessments, create solution designs, and lead implementation teams."},
    {"job_title": "Platform Engineer", "company": "Thoughtworks", "location": "Pune, India", "category": "DevOps", "experience_level": "Mid Level", "salary_range": "14-25 LPA",
     "required_skills": "kubernetes, docker, helm, argocd, terraform, github actions, linux, python, go, observability",
     "description": "Thoughtworks is hiring a Platform Engineer to build and maintain internal developer platforms. You will create self-service infrastructure, implement GitOps workflows, and improve developer experience."},

    # Mobile Development
    {"job_title": "Android Developer", "company": "Paytm", "location": "Noida, India", "category": "Mobile Development", "experience_level": "Entry Level", "salary_range": "5-10 LPA",
     "required_skills": "kotlin, android sdk, java, xml, retrofit, room, mvvm, git, firebase",
     "description": "Paytm is looking for an Android Developer to build features for India's leading digital payment app. You will develop UI components, integrate REST APIs, and write testable code following MVVM architecture."},
    {"job_title": "iOS Developer", "company": "Meesho", "location": "Bangalore, India", "category": "Mobile Development", "experience_level": "Mid Level", "salary_range": "12-22 LPA",
     "required_skills": "swift, swift ui, ios sdk, xcode, core data, combine, rest api, git, ci/cd",
     "description": "Meesho seeks an iOS Developer to build and enhance our e-commerce app used by millions. You will implement SwiftUI views, optimize app performance, and ensure smooth user experiences on Apple devices."},
    {"job_title": "Flutter Developer", "company": "Dream11", "location": "Mumbai, India", "category": "Mobile Development", "experience_level": "Mid Level", "salary_range": "10-18 LPA",
     "required_skills": "flutter, dart, firebase, rest api, state management, git, ui design, testing",
     "description": "Dream11 is hiring a Flutter Developer to build cross-platform mobile experiences for our fantasy sports platform. You will create responsive UIs, manage app state, and integrate real-time data feeds."},
    {"job_title": "React Native Developer", "company": "Myntra", "location": "Bangalore, India", "category": "Mobile Development", "experience_level": "Entry Level", "salary_range": "6-12 LPA",
     "required_skills": "react native, javascript, typescript, redux, rest api, git, expo, firebase",
     "description": "Myntra seeks a React Native Developer to work on our fashion e-commerce mobile app. You will build reusable components, optimize performance, and collaborate with backend teams for seamless integration."},
    {"job_title": "Mobile Lead", "company": "CRED", "location": "Bangalore, India", "category": "Mobile Development", "experience_level": "Senior Level", "salary_range": "30-50 LPA",
     "required_skills": "kotlin, swift, flutter, system design, leadership, mentoring, ci/cd, architecture, performance optimization",
     "description": "CRED is looking for a Mobile Lead to oversee the entire mobile engineering function. You will define mobile architecture, mentor a team of developers, and drive technical excellence across iOS and Android platforms."},

    # Cybersecurity
    {"job_title": "Security Analyst", "company": "Tata AIG", "location": "Mumbai, India", "category": "Cybersecurity", "experience_level": "Entry Level", "salary_range": "4-8 LPA",
     "required_skills": "networking, linux, firewall, siem, vulnerability assessment, python, security, owasp, communication",
     "description": "Tata AIG is hiring a Security Analyst to monitor and respond to security incidents. You will analyze security logs, conduct vulnerability assessments, and help maintain the organization's security posture."},
    {"job_title": "Penetration Tester", "company": "Astra Security", "location": "Remote", "category": "Cybersecurity", "experience_level": "Mid Level", "salary_range": "8-16 LPA",
     "required_skills": "penetration testing, burp suite, owasp, linux, python, networking, web security, report writing, ceh",
     "description": "Astra Security seeks a Penetration Tester to identify vulnerabilities in client web applications. You will perform manual and automated security testing, write detailed reports, and recommend remediation steps."},
    {"job_title": "SOC Analyst", "company": "IBM", "location": "Bangalore, India", "category": "Cybersecurity", "experience_level": "Entry Level", "salary_range": "5-9 LPA",
     "required_skills": "siem, splunk, networking, incident response, linux, windows server, threat analysis, communication",
     "description": "IBM is hiring a SOC Analyst to monitor security events in our 24/7 Security Operations Center. You will investigate alerts, escalate incidents, and create threat intelligence reports."},
    {"job_title": "Cloud Security Engineer", "company": "Palo Alto Networks", "location": "Bangalore, India", "category": "Cybersecurity", "experience_level": "Senior Level", "salary_range": "25-45 LPA",
     "required_skills": "aws, azure, cloud security, iam, terraform, zero trust, compliance, cissp, kubernetes security",
     "description": "Palo Alto Networks is looking for a Cloud Security Engineer to secure cloud-native environments. You will design security architectures, implement zero-trust models, and ensure compliance with industry standards."},
    {"job_title": "Application Security Engineer", "company": "Zomato", "location": "Gurugram, India", "category": "Cybersecurity", "experience_level": "Mid Level", "salary_range": "14-25 LPA",
     "required_skills": "owasp, code review, python, java, security testing, ci/cd, docker, threat modeling, sdlc",
     "description": "Zomato is hiring an AppSec Engineer to embed security into our development lifecycle. You will conduct code reviews, run SAST/DAST tools, perform threat modeling, and train developers on secure coding."},

    # Database & Backend
    {"job_title": "Database Administrator", "company": "Oracle", "location": "Hyderabad, India", "category": "Database", "experience_level": "Mid Level", "salary_range": "10-18 LPA",
     "required_skills": "oracle, mysql, postgresql, sql, database tuning, backup, replication, linux, python, monitoring",
     "description": "Oracle is seeking a Database Administrator to manage enterprise database systems. You will optimize query performance, manage backups, implement replication strategies, and ensure data integrity across environments."},
    {"job_title": "Data Engineer", "company": "Uber", "location": "Hyderabad, India", "category": "Database", "experience_level": "Mid Level", "salary_range": "18-32 LPA",
     "required_skills": "python, sql, spark, hadoop, airflow, kafka, aws, data modeling, etl, data pipeline",
     "description": "Uber is hiring a Data Engineer to build and maintain large-scale data pipelines. You will design ETL processes, optimize Spark jobs, and ensure reliable data delivery for analytics and ML teams."},
    {"job_title": "ETL Developer", "company": "Capgemini", "location": "Pune, India", "category": "Database", "experience_level": "Entry Level", "salary_range": "4-8 LPA",
     "required_skills": "sql, python, etl, informatica, data warehouse, mysql, oracle, data quality, problem solving",
     "description": "Capgemini is looking for an ETL Developer to build data transformation pipelines. You will extract data from multiple sources, transform it using business rules, and load it into data warehouses."},

    # Product & Management
    {"job_title": "Product Manager", "company": "Atlassian", "location": "Bangalore, India", "category": "Product Management", "experience_level": "Mid Level", "salary_range": "20-35 LPA",
     "required_skills": "product management, user research, data analysis, sql, communication, leadership, agile, roadmapping, a/b testing",
     "description": "Atlassian is hiring a Product Manager to drive the strategy and roadmap for our collaboration tools. You will define product requirements, analyze user data, run A/B tests, and work cross-functionally with engineering and design."},
    {"job_title": "Technical Project Manager", "company": "HCL", "location": "Noida, India", "category": "Product Management", "experience_level": "Mid Level", "salary_range": "12-20 LPA",
     "required_skills": "project management, agile, scrum, jira, communication, leadership, risk management, pmp, budgeting",
     "description": "HCL seeks a Technical Project Manager to lead software delivery projects. You will manage timelines, budgets, and stakeholder expectations, ensuring on-time delivery using Agile/Scrum methodologies."},
    {"job_title": "Scrum Master", "company": "ThoughtSpot", "location": "Hyderabad, India", "category": "Product Management", "experience_level": "Mid Level", "salary_range": "14-22 LPA",
     "required_skills": "scrum, agile, facilitation, jira, confluence, communication, coaching, continuous improvement, kanban",
     "description": "ThoughtSpot is hiring a Scrum Master to facilitate agile ceremonies and remove blockers for engineering teams. You will coach teams on Scrum practices, track velocity, and drive continuous process improvement."},

    # QA & Testing
    {"job_title": "QA Engineer", "company": "Freshworks", "location": "Chennai, India", "category": "Testing", "experience_level": "Entry Level", "salary_range": "4-8 LPA",
     "required_skills": "testing, selenium, java, python, sql, bug tracking, jira, test cases, communication",
     "description": "Freshworks is looking for a QA Engineer to ensure software quality. You will write test cases, automate tests using Selenium, log defects in Jira, and collaborate with developers to resolve issues."},
    {"job_title": "Automation Test Engineer", "company": "Wipro", "location": "Bangalore, India", "category": "Testing", "experience_level": "Mid Level", "salary_range": "8-15 LPA",
     "required_skills": "selenium, python, java, cypress, playwright, ci/cd, jenkins, api testing, postman, git",
     "description": "Wipro is hiring an Automation Test Engineer to build and maintain test automation frameworks. You will write end-to-end tests using Selenium and Cypress, integrate with CI/CD pipelines, and perform API testing."},
    {"job_title": "Performance Test Engineer", "company": "Publicis Sapient", "location": "Gurugram, India", "category": "Testing", "experience_level": "Mid Level", "salary_range": "10-18 LPA",
     "required_skills": "jmeter, gatling, load testing, performance tuning, apm, linux, python, sql, monitoring, grafana",
     "description": "Publicis Sapient seeks a Performance Test Engineer to ensure application scalability. You will design load test scripts in JMeter, analyze bottlenecks, and recommend performance optimizations."},

    # Emerging Tech
    {"job_title": "Blockchain Developer", "company": "Polygon", "location": "Bangalore, India", "category": "Blockchain", "experience_level": "Mid Level", "salary_range": "15-30 LPA",
     "required_skills": "solidity, ethereum, web3, javascript, smart contracts, rust, go, cryptography, git",
     "description": "Polygon is hiring a Blockchain Developer to build smart contracts and decentralized applications. You will design secure Solidity contracts, implement Layer-2 scaling solutions, and contribute to open-source protocols."},
    {"job_title": "IoT Engineer", "company": "Bosch", "location": "Bangalore, India", "category": "IoT", "experience_level": "Entry Level", "salary_range": "5-10 LPA",
     "required_skills": "python, c, embedded systems, mqtt, aws iot, raspberry pi, arduino, linux, networking, sensors",
     "description": "Bosch is looking for an IoT Engineer to develop connected device solutions. You will program embedded systems, set up MQTT communication, and integrate sensors with cloud platforms for real-time data processing."},
    {"job_title": "AR/VR Developer", "company": "Flipkart", "location": "Bangalore, India", "category": "AR/VR", "experience_level": "Mid Level", "salary_range": "12-22 LPA",
     "required_skills": "unity, c#, 3d modeling, ar kit, ar core, game development, mathematics, shaders, optimization",
     "description": "Flipkart is hiring an AR/VR Developer to create immersive shopping experiences. You will build augmented reality features using Unity and ARCore, enabling customers to visualize products in their space."},
]

# Generate additional variations to reach ~200 jobs
def generate_more_jobs(base_jobs):
    extra_companies = [
        "Cognizant", "Mindtree", "L&T Infotech", "Mphasis", "Tech Mahindra",
        "Hexaware", "Persistent Systems", "Cyient", "Zensar Technologies",
        "Birlasoft", "Coforge", "NIIT Technologies", "Saksoft", "Happiest Minds",
        "Mu Sigma", "Fractal Analytics", "AbsoluteData", "Tiger Analytics",
        "LatentView Analytics", "MiQ Digital", "Sigmoid", "Tredence",
        "PayU", "BrowserStack", "Postman", "Groww", "Cred", "Lenskart",
        "Dunzo", "Rapido", "Urban Company", "Nykaa", "BigBasket",
        "ShareChat", "Verse Innovation", "Josh", "Glance", "InMobi",
        "CleverTap", "MoEngage", "WebEngage", "Freshworks", "Chargebee"
    ]
    
    extra_cities = [
        "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Pune, India",
        "Delhi, India", "Chennai, India", "Noida, India", "Gurugram, India",
        "Kolkata, India", "Ahmedabad, India", "Remote"
    ]
    
    title_variations = {
        "Software Engineering": [
            "Associate Software Engineer", "Software Engineer II", "Staff Engineer",
            "Principal Engineer", "Solutions Engineer", "Application Developer"
        ],
        "Data Science": [
            "Junior Data Analyst", "Senior Data Scientist", "Analytics Engineer",
            "Quantitative Analyst", "NLP Engineer", "Computer Vision Engineer"
        ],
        "Web Development": [
            "Web Developer", "Frontend Engineer", "JavaScript Developer",
            "Vue.js Developer", "Next.js Developer", "UI Engineer"
        ],
        "DevOps": [
            "Infrastructure Engineer", "Release Engineer", "Build Engineer",
            "Cloud Engineer", "Systems Engineer", "Automation Engineer"
        ],
        "Mobile Development": [
            "Mobile Developer", "Cross-Platform Developer", "Mobile QA Engineer"
        ],
        "Cybersecurity": [
            "Information Security Analyst", "Security Engineer", "Cyber Threat Analyst"
        ]
    }
    
    all_jobs = list(base_jobs)
    
    for job in base_jobs:
        category = job["category"]
        if category in title_variations:
            for new_title in title_variations[category][:2]:
                new_job = dict(job)
                new_job["job_title"] = new_title
                new_job["company"] = random.choice(extra_companies)
                new_job["location"] = random.choice(extra_cities)
                all_jobs.append(new_job)
    
    return all_jobs

def main():
    all_jobs = generate_more_jobs(JOBS)
    
    # Shuffle for variety
    random.seed(42)
    random.shuffle(all_jobs)
    
    # Add ID column
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "jobs_dataset.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "job_title", "company", "location", "category",
            "experience_level", "salary_range", "required_skills", "description"
        ])
        writer.writeheader()
        for idx, job in enumerate(all_jobs, 1):
            row = {"id": idx}
            row.update(job)
            writer.writerow(row)
    
    print(f"Generated {len(all_jobs)} jobs -> {output_path}")

if __name__ == "__main__":
    main()
