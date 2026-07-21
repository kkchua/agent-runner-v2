import flet as ft

def main(page: ft.Page):
    page.title = "Sample Dropdown App"
    
    # Sample data - similar to how repos and workflows are structured
    repo_to_workflows = {
        "Repo A": ["Workflow 1", "Workflow 2", "Workflow 3"],
        "Repo B": ["Workflow 4", "Workflow 5"],
        "Repo C": ["Workflow 6", "Workflow 7", "Workflow 8", "Workflow 9"]
    }
    
    def on_repo_changed(e):
        print(f"Repo changed to: {repo_dd.value}")
        # Clear and update workflow dropdown based on selected repo
        workflow_dd.options = [ft.dropdown.Option(wf) for wf in repo_to_workflows.get(repo_dd.value, [])]
        if repo_to_workflows.get(repo_dd.value):
            workflow_dd.value = repo_to_workflows[repo_dd.value][0]
        else:
            workflow_dd.value = None
        page.update()
        print(f"Updated workflow options: {[opt.key for opt in workflow_dd.options]}")
    
    # Initialize dropdowns
    repo_dd = ft.Dropdown(
        label="Repository",
        options=[ft.dropdown.Option(repo) for repo in repo_to_workflows.keys()],
        on_change=on_repo_changed,
        width=200
    )
    
    workflow_dd = ft.Dropdown(
        label="Workflow",
        options=[ft.dropdown.Option(wf) for wf in repo_to_workflows["Repo A"]],  # Default to first repo's workflows
        width=200
    )
    
    # Set initial value for workflow dropdown
    workflow_dd.value = repo_to_workflows["Repo A"][0]
    
    page.add(
        ft.Text("Sample Dropdown App - Repo to Workflow Mapping", size=20),
        ft.Row([repo_dd, workflow_dd])
    )
    
    # Log initial state
    print("App initialized")
    print(f"Initial repo options: {[opt.key for opt in repo_dd.options]}")
    print(f"Initial workflow options: {[opt.key for opt in workflow_dd.options]}")

if __name__ == "__main__":
    ft.app(target=main)