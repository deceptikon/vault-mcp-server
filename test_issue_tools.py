import sys
import os
from pathlib import Path
from datetime import datetime

# Add the server directory to path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_issue, start_issue, finish_issue, read_issue, update_issue, move_issue, get_vault_path, list_issues

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

    # 2. Test list_issues (inbox)
    print("\n2. Testing list_issues('inbox')...")
    inbox_list = list_issues("inbox")
    if iss_uniq_id in inbox_list:
        print(f"Verification: Created issue {iss_uniq_id} found in inbox.")
    else:
        print(f"Verification: Created issue {iss_uniq_id} NOT found in inbox list.")

    # 3. Test read_issue
    print(f"\n3. Testing read_issue with ID='{iss_uniq_id}'...")
    content = read_issue(iss_uniq_id)
    if "Error" in content:
        print(f"Read issue failed: {content}")
        return
    print(f"Verification: Read content (snippet): {content[:50]}...")
    if f"ID: {iss_uniq_id}" in content:
        print("Verification: ID found in content.")

    # 4. Test update_issue (append) with ID='{iss_uniq_id}'
    print(f"\n4. Testing update_issue (append) with ID='{iss_uniq_id}'...")
    append_text = "\n%% Appended verification tag %%"
    update_result = update_issue(iss_uniq_id, append_text, append=True)
    print(f"Result: {update_result}")
    
    updated_content = read_issue(iss_uniq_id)
    if append_text in updated_content:
        print("Verification: Content correctly appended.")
    else:
        print("Verification: Append FAILED.")

    # 5. Test start_issue (moves to processing)
    print(f"\n5. Testing start_issue with ID='{iss_uniq_id}'...")
    start_result = start_issue(iss_uniq_id)
    print(f"Result: {start_result[:100]}...")
    
    if "Error" in start_result:
        print(f"Start issue failed: {start_result}")
        return
        
    # Verify it's in processing
    processing_list = list_issues("processing")
    if iss_uniq_id in processing_list:
        print(f"Verification: Issue {iss_uniq_id} found in processing.")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in processing.")

    # 6. Test move_issue (to finished)
    print(f"\n6. Testing move_issue to 'finished' with ID='{iss_uniq_id}'...")
    move_result = move_issue(iss_uniq_id, "finished")
    print(f"Result: {move_result}")
    
    finished_list = list_issues("finished")
    if iss_uniq_id in finished_list:
        print(f"Verification: Issue {iss_uniq_id} found in finished.")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in finished.")

    # 7. Test finish_issue (moves to review and adds timestamp)
    print(f"\n7. Testing finish_issue with ID='{iss_uniq_id}'...")
    finish_result = finish_issue(iss_uniq_id)
    print(f"Result: {finish_result}")
    
    if "Error" in finish_result:
        print(f"Finish issue failed: {finish_result}")
        return
        
    review_list = list_issues("review")
    if iss_uniq_id in review_list:
        print(f"Verification: Issue {iss_uniq_id} found in review.")
        content = read_issue(iss_uniq_id)
        if "%% Finished:" in content:
            print("Verification: Finished timestamp found.")
        else:
            print("Verification: Finished timestamp NOT found.")
        
        # Cleanup
        # Find the actual path to delete it
        from main import _find_issue_path
        found_file = _find_issue_path(iss_uniq_id)
        if found_file:
            os.remove(found_file)
            print(f"Cleanup: Removed {found_file}")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in review.")

if __name__ == "__main__":
    test_harmonized_workflow()
