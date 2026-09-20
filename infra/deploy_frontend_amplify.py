import os
import io
import time
import zipfile
import boto3
import requests

REGION = "ap-south-1"
APP_NAME = "pramaan-frontend"
BRANCH_NAME = "main"
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

# Official AWS Amplify SPA rewrite rule for React Router
CUSTOM_RULES = [
    {
        "source": "</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json)$)([^.]+$)/>",
        "target": "/index.html",
        "status": "200"
    }
]

def create_dist_zip():
    print(f"Creating zip from: {DIST_DIR}")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR).replace("\\", "/")
                zf.write(full_path, rel_path)
    buf.seek(0)
    return buf.getvalue()

def deploy():
    if not os.path.isdir(DIST_DIR):
        raise FileNotFoundError(f"Dist directory not found at {DIST_DIR}. Run 'npm run build' first.")

    amplify = boto3.client("amplify", region_name=REGION)

    # 1. Find or create Amplify app
    app_id = None
    default_domain = None
    apps = amplify.list_apps()
    for a in apps.get("apps", []):
        if a.get("name") == APP_NAME:
            app_id = a["appId"]
            default_domain = a.get("defaultDomain")
            print(f"Found existing Amplify App: {app_id}")
            break

    if not app_id:
        print(f"Creating AWS Amplify App: {APP_NAME}...")
        created = amplify.create_app(
            name=APP_NAME,
            platform="WEB",
            customRules=CUSTOM_RULES,
            description="Pramaan Intelligent Document Verification Web App"
        )
        app_id = created["app"]["appId"]
        default_domain = created["app"]["defaultDomain"]
        print(f"Created Amplify App: {app_id}")
    else:
        # Update custom rules for SPA routing
        amplify.update_app(appId=app_id, customRules=CUSTOM_RULES)

    # 2. Find or create branch
    try:
        amplify.get_branch(appId=app_id, branchName=BRANCH_NAME)
        print(f"Branch '{BRANCH_NAME}' already exists.")
    except Exception:
        print(f"Creating branch '{BRANCH_NAME}'...")
        amplify.create_branch(appId=app_id, branchName=BRANCH_NAME)

    # 3. Create deployment
    print("Initiating deployment...")
    dep = amplify.create_deployment(appId=app_id, branchName=BRANCH_NAME)
    job_id = dep["jobId"]
    upload_url = dep["zipUploadUrl"]

    # 4. Upload zip
    print("Uploading production bundle to AWS Amplify...")
    zip_data = create_dist_zip()
    res = requests.put(upload_url, data=zip_data, headers={"Content-Type": "application/zip"})
    if res.status_code != 200:
        raise RuntimeError(f"Failed to upload zip: {res.status_code} {res.text}")
    print("Bundle uploaded successfully.")

    # 5. Start deployment
    print("Deploying bundle to AWS edge...")
    amplify.start_deployment(appId=app_id, branchName=BRANCH_NAME, jobId=job_id)

    # 6. Poll for completion
    https_url = f"https://{BRANCH_NAME}.{default_domain}"
    print("Waiting for deployment to complete...")
    for _ in range(30):
        time.sleep(2)
        job = amplify.get_job(appId=app_id, branchName=BRANCH_NAME, jobId=job_id)
        status = job["job"]["summary"]["status"]
        print(f"  Status: {status}")
        if status == "SUCCEED":
            print("\n" + "="*60)
            print("SUCCESS: PRAMAAN FRONTEND IS LIVE WITH HTTPS ON AWS!")
            print(f"URL: {https_url}")
            print("="*60)
            return https_url
        elif status == "FAILED":
            raise RuntimeError("Deployment failed on AWS Amplify.")

    print(f"Deployment is still processing. Live URL will be: {https_url}")
    return https_url

if __name__ == "__main__":
    deploy()
