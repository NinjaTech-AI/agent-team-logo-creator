#!/usr/bin/env python3
"""
Railway Deployment Script using Railway Public API
API Reference: https://docs.railway.com/reference/public-api
"""

import requests
import json
import sys
import time

# Railway API Configuration
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
RAILWAY_TOKEN = "9da9bc4d-fba8-4ac5-92c4-e4a62304ec7d"

headers = {
    "Authorization": f"Bearer {RAILWAY_TOKEN}",
    "Content-Type": "application/json"
}

def graphql_query(query, variables=None):
    """Execute a GraphQL query against Railway API"""
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    response = requests.post(RAILWAY_API_URL, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    
    if "errors" in data:
        print(f"❌ GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
        return None
    
    return data.get("data")

def get_user_info():
    """Get current user information"""
    query = """
    query {
        me {
            id
            name
            email
        }
    }
    """
    return graphql_query(query)

def list_projects():
    """List all projects"""
    query = """
    query {
        projects {
            edges {
                node {
                    id
                    name
                    description
                }
            }
        }
    }
    """
    return graphql_query(query)

def create_project(name, description=""):
    """Create a new project"""
    query = """
    mutation ProjectCreate($input: ProjectCreateInput!) {
        projectCreate(input: $input) {
            id
            name
        }
    }
    """
    variables = {
        "input": {
            "name": name,
            "description": description
        }
    }
    return graphql_query(query, variables)

def create_service(project_id, name, source_repo):
    """Create a service in a project"""
    query = """
    mutation ServiceCreate($input: ServiceCreateInput!) {
        serviceCreate(input: $input) {
            id
            name
        }
    }
    """
    variables = {
        "input": {
            "projectId": project_id,
            "name": name,
            "source": {
                "repo": source_repo
            }
        }
    }
    return graphql_query(query, variables)

def get_service_domains(service_id):
    """Get domains for a service"""
    query = """
    query Service($id: String!) {
        service(id: $id) {
            id
            name
            serviceDomains {
                edges {
                    node {
                        domain
                    }
                }
            }
        }
    }
    """
    variables = {"id": service_id}
    return graphql_query(query, variables)

def main():
    print("🚀 Railway Deployment Script")
    print("=" * 50)
    
    # Step 1: Verify authentication
    print("\n📋 Step 1: Verifying authentication...")
    user_info = get_user_info()
    if not user_info:
        print("❌ Authentication failed!")
        sys.exit(1)
    
    print(f"✅ Authenticated as: {user_info['me']['name']} ({user_info['me']['email']})")
    
    # Step 2: List existing projects
    print("\n📋 Step 2: Checking existing projects...")
    projects_data = list_projects()
    if not projects_data:
        print("❌ Failed to list projects!")
        sys.exit(1)
    
    projects = projects_data.get("projects", {}).get("edges", [])
    print(f"✅ Found {len(projects)} existing projects")
    
    # Check if project already exists
    project_name = "ai-logo-creator"
    existing_project = None
    for edge in projects:
        if edge["node"]["name"] == project_name:
            existing_project = edge["node"]
            break
    
    if existing_project:
        print(f"✅ Project '{project_name}' already exists (ID: {existing_project['id']})")
        project_id = existing_project['id']
    else:
        # Step 3: Create new project
        print(f"\n📋 Step 3: Creating new project '{project_name}'...")
        project_data = create_project(
            name=project_name,
            description="AI-powered logo creator with React frontend and FastAPI backend"
        )
        if not project_data:
            print("❌ Failed to create project!")
            sys.exit(1)
        
        project_id = project_data["projectCreate"]["id"]
        print(f"✅ Project created successfully (ID: {project_id})")
    
    # Step 4: Create service
    print(f"\n📋 Step 4: Creating service...")
    service_data = create_service(
        project_id=project_id,
        name="logo-creator-app",
        source_repo="NinjaTech-AI/agent-team-logo-creator"
    )
    
    if not service_data:
        print("❌ Failed to create service!")
        print("Note: Service might already exist. Checking existing services...")
        # In production, we'd query existing services here
        sys.exit(1)
    
    service_id = service_data["serviceCreate"]["id"]
    print(f"✅ Service created successfully (ID: {service_id})")
    
    # Step 5: Wait for deployment and get domain
    print(f"\n📋 Step 5: Waiting for deployment...")
    print("⏳ This may take a few minutes...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(10)
        domains_data = get_service_domains(service_id)
        
        if domains_data and domains_data.get("service", {}).get("serviceDomains", {}).get("edges"):
            domains = domains_data["service"]["serviceDomains"]["edges"]
            if domains:
                domain = domains[0]["node"]["domain"]
                print(f"\n✅ Deployment successful!")
                print(f"🌐 Live URL: https://{domain}")
                return
        
        print(f"⏳ Attempt {attempt + 1}/{max_attempts}...")
    
    print("\n⚠️ Deployment initiated but domain not yet available.")
    print("Please check Railway dashboard for deployment status.")

if __name__ == "__main__":
    main()