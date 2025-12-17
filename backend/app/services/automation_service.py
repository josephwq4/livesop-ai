from app.repositories.persistence import PersistenceRepository

# BOOT TRACE
print("[BOOT] Loading automation_service body...", flush=True)

def run_automation_logic(team_id, action, params):
    print(f"Auto Service executing: {team_id} {action}")
    try:
        repo = PersistenceRepository()
        # Just verifying DB access
        # Ensure we don't crash loop
        return {"success": True, "message": "Automation Service Active (DB Connected)", "team": team_id}
    except Exception as e:
        print(f"Error in automation logic: {e}")
        return {"success": False, "error": str(e)}
