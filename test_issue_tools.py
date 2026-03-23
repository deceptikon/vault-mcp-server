import sys
import os
from pathlib import Path
from datetime import datetime

# Add the server directory to path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_issue, start_issue, finish_issue, read_issue, update_issue, move_issue, get_vault_path

def test_harmonized_workflow():
    print("Starting Harmonized Vault Workflow Test...")
    
    # Test parameters
    issue_name = "harmonized_test_issue"
    issue_body = "This is a test issue for the harmonized vault MCP."
    issue_tags = ["test", "harmonized"]
    
    # 1. Test create_issue
    print(f"\n1. Testing create_issue with name='{issue_name}'...")
    iss_uniq_id = create_issue(issue_name, issue_body, issue_tags)
    print(f"Result (Unique ID): {iss_uniq_id}")
    
    if "Error" in iss_uniq_id:
        print(f"Create issue failed: {iss_uniq_id}")
        return

    # 2. Test read_issue
    print(f"\n2. Testing read_issue with ID='{iss_uniq_id}'...")
    content = read_issue(iss_uniq_id)
    if "Error" in content:
        print(f"Read issue failed: {content}")
        return
    print(f"Verification: Read content (snippet): {content[:50]}...")
    if f"ID: {iss_uniq_id}" in content:
        print("Verification: ID found in content.")

    # 3. Test update_issue
    print(f"\n3. Testing update_issue (append) with ID='{iss_uniq_id}'...")
    append_text = "\n%% Appended verification tag %%"
    update_result = update_issue(iss_uniq_id, append_text, append=True)
    print(f"Result: {update_result}")
    
    updated_content = read_issue(iss_uniq_id)
    if append_text in updated_content:
        print("Verification: Content correctly appended.")
    else:
        print("Verification: Append FAILED.")

    # 4. Test start_issue (moves to 20_Processing)
    print(f"\n4. Testing start_issue with ID='{iss_uniq_id}'...")
    start_result = start_issue(iss_uniq_id)
    print(f"Result: {start_result[:100]}...")
    
    if "Error" in start_result:
        print(f"Start issue failed: {start_result}")
        return
        
    vault_root = get_vault_path()
    # Find the file to verify its location
    found_file = None
    for file in (vault_root / "20_Processing").glob(f"*{iss_uniq_id}*.md"):
        found_file = file
        break
    
    if found_file:
        print(f"Verification: File successfully moved to 20_Processing: {found_file.name}")
    else:
        print("Verification: File NOT found in 20_Processing.")

    # 5. Test move_issue (to 999_Finished)
    print(f"\n5. Testing move_issue to 999_Finished with ID='{iss_uniq_id}'...")
    move_result = move_issue(iss_uniq_id, "999_Finished")
    print(f"Result: {move_result}")
    
    found_file = None
    for file in (vault_root / "999_Finished").glob(f"*{iss_uniq_id}*.md"):
        found_file = file
        break
    
    if found_file:
        print(f"Verification: File successfully moved to 999_Finished: {found_file.name}")
    else:
        print("Verification: File NOT found in 999_Finished.")

    # 6. Test finish_issue (moves to 30_ToReview and adds timestamp)
    print(f"\n6. Testing finish_issue with ID='{iss_uniq_id}'...")
    finish_result = finish_issue(iss_uniq_id)
    print(f"Result: {finish_result}")
    
    if "Error" in finish_result:
        print(f"Finish issue failed: {finish_result}")
        return
        
    found_file = None
    for file in (vault_root / "30_ToReview").glob(f"*{iss_uniq_id}*.md"):
        found_file = file
        break
    
    if found_file:
        print(f"Verification: File successfully moved to 30_ToReview: {found_file.name}")
        content = found_file.read_text()
        if "%% Finished:" in content:
            print("Verification: Finished timestamp found.")
        else:
            print("Verification: Finished timestamp NOT found.")
        
        # Cleanup
        os.remove(found_file)
        print(f"Cleanup: Removed {found_file}")
    else:
        print("Verification: File NOT found in 30_ToReview.")

if __name__ == "__main__":
    test_harmonized_workflow()
