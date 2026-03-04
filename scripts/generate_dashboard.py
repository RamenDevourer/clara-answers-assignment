import os
import json

def generate_dashboard():
    base_dir = "/data"
    accounts_dir = os.path.join(base_dir, "outputs", "accounts")
    changelog_dir = os.path.join(base_dir, "changelog")
    
    accounts = []
    total_changes = 0
    
    if os.path.exists(accounts_dir):
        for acc in os.listdir(accounts_dir):
            acc_path = os.path.join(accounts_dir, acc)
            if os.path.isdir(acc_path):
                has_v1 = os.path.exists(os.path.join(acc_path, "v1", "memo.json"))
                has_v2 = os.path.exists(os.path.join(acc_path, "v2", "memo.json"))
                
                changes = []
                cl_path = os.path.join(changelog_dir, acc, "changes.json")
                if os.path.exists(cl_path):
                    with open(cl_path, "r") as f:
                        changes = json.load(f)
                        total_changes += len(changes)
                        
                accounts.append({
                    "id": acc,
                    "v1": has_v1,
                    "v2": has_v2,
                    "changes": changes
                })

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clara Answers - Deployment Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }}
            h1 {{ color: #2c3e50; }}
            .metrics {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .metric-card {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; text-align: center; }}
            .metric-card h3 {{ margin: 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }}
            .metric-card p {{ margin: 10px 0 0; font-size: 24px; font-weight: bold; color: #2980b9; }}
            table {{ width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 40px; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #2c3e50; color: #fff; }}
            .status-yes {{ color: #27ae60; font-weight: bold; }}
            .status-no {{ color: #c0392b; font-weight: bold; }}
            .diff-viewer {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .diff-item {{ margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
            del {{ color: #c0392b; background: #fadbd8; text-decoration: none; padding: 2px 4px; border-radius: 3px; }}
            ins {{ color: #27ae60; background: #d5f5e3; text-decoration: none; padding: 2px 4px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>Clara Answers Deployments</h1>
        
        <div class="metrics">
            <div class="metric-card"><h3>Total Accounts</h3><p>{len(accounts)}</p></div>
            <div class="metric-card"><h3>v1 Generated</h3><p>{sum(1 for a in accounts if a['v1'])}</p></div>
            <div class="metric-card"><h3>v2 Updated</h3><p>{sum(1 for a in accounts if a['v2'])}</p></div>
            <div class="metric-card"><h3>Total Changes Tracked</h3><p>{total_changes}</p></div>
        </div>

        <h2>Account Status</h2>
        <table>
            <tr><th>Account ID</th><th>Pipeline A (v1)</th><th>Pipeline B (v2)</th><th>Changes</th></tr>
            {"".join(f"<tr><td>{a['id']}</td><td class='{'status-yes' if a['v1'] else 'status-no'}'>{'Complete' if a['v1'] else 'Pending'}</td><td class='{'status-yes' if a['v2'] else 'status-no'}'>{'Complete' if a['v2'] else 'Pending'}</td><td>{len(a['changes'])} updates</td></tr>" for a in accounts)}
        </table>

        <h2>Diff Viewer (Changelogs)</h2>
        <div class="diff-viewer">
    """
    
    for acc in accounts:
        if acc['changes']:
            html += f"<h3>{acc['id']}</h3>"
            for change in acc['changes']:
                old_v = json.dumps(change['old_value']) if isinstance(change['old_value'], (dict, list)) else str(change['old_value'])
                new_v = json.dumps(change['new_value']) if isinstance(change['new_value'], (dict, list)) else str(change['new_value'])
                html += f"""
                <div class="diff-item">
                    <strong>File:</strong> {change['file']} | <strong>Field:</strong> {change['field']}<br>
                    <del>- {old_v}</del><br>
                    <ins>+ {new_v}</ins><br>
                    <em>Reason: {change['reason']}</em>
                </div>
                """

    html += """
        </div>
    </body>
    </html>
    """

    output_path = os.path.join(base_dir, "outputs", "dashboard.html")
    with open(output_path, "w") as f:
        f.write(html)
        
    print(json.dumps({"status": "Dashboard generated successfully", "path": output_path}))

if __name__ == "__main__":
    generate_dashboard()