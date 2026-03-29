import sys
import os
from pathlib import Path

# Add the server directory to path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    create_issue,
    read_issue,
    update_issue,
    move_issue,
    list_issues,
    get_vault_path,
    _find_issue_path,
    get_status,
    search_vault,
)


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
        return iss_uniq_id

    # 2. Test list_issues (inbox)
    print("\n2. Testing list_issues('10_Inbox')...")
    inbox_list = list_issues("10_Inbox")
    if iss_uniq_id in inbox_list:
        print(f"Verification: Created issue {iss_uniq_id} found in inbox.")
    else:
        print(f"Verification: Created issue {iss_uniq_id} NOT found in inbox list.")

    # 3. Test read_issue
    print(f"\n3. Testing read_issue with ID='{iss_uniq_id}'...")
    content = read_issue(iss_uniq_id)
    if "Error" in content:
        print(f"Read issue failed: {content}")
        return iss_uniq_id
    print(f"Verification: Read content (snippet): {content[:50]}...")
    if f"ID: {iss_uniq_id}" in content:
        print("Verification: ID found in content.")

    # 4. Test update_issue (append)
    print(f"\n4. Testing update_issue (append) with ID='{iss_uniq_id}'...")
    append_text = "\n%% Appended verification tag %%"
    update_result = update_issue(iss_uniq_id, append_text, append=True)
    print(f"Result: {update_result}")

    updated_content = read_issue(iss_uniq_id)
    if append_text in updated_content:
        print("Verification: Content correctly appended.")
    else:
        print("Verification: Append FAILED.")

    # 5. Test move_issue (to processing)
    print(f"\n5. Testing move_issue to '20_Processing' with ID='{iss_uniq_id}'...")
    move_result = move_issue(iss_uniq_id, "20_Processing")
    print(f"Result: {move_result}")

    if "Error" in move_result:
        print(f"Move issue failed: {move_result}")
        return iss_uniq_id

    # Verify it's in processing
    processing_list = list_issues("20_Processing")
    if iss_uniq_id in processing_list:
        print(f"Verification: Issue {iss_uniq_id} found in processing.")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in processing.")

    # 6. Test move_issue (to finished)
    print(f"\n6. Testing move_issue to '999_Finished' with ID='{iss_uniq_id}'...")
    move_result = move_issue(iss_uniq_id, "999_Finished")
    print(f"Result: {move_result}")

    finished_list = list_issues("999_Finished")
    if iss_uniq_id in finished_list:
        print(f"Verification: Issue {iss_uniq_id} found in finished.")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in finished.")

    # 7. Test move_issue (to review)
    print(f"\n7. Testing move_issue to '30_ToReview' with ID='{iss_uniq_id}'...")
    move_result = move_issue(iss_uniq_id, "30_ToReview")
    print(f"Result: {move_result}")

    review_list = list_issues("30_ToReview")
    if iss_uniq_id in review_list:
        print(f"Verification: Issue {iss_uniq_id} found in review.")
    else:
        print(f"Verification: Issue {iss_uniq_id} NOT found in review.")

    # 8. Test get_status
    print("\n8. Testing get_status()...")
    status = get_status()
    if "Error" in status:
        print(f"Get status failed: {status}")
    else:
        print("Verification: get_status() returned content.")
        if "30_ToReview" in status and iss_uniq_id in status:
            print("Verification: Issue found in status overview.")

    # 9. Test search_vault
    print("\n9. Testing search_vault()...")
    search_result = search_vault("harmonized")
    if "Error" in search_result:
        print(f"Search failed: {search_result}")
    else:
        print(f"Verification: search_vault() returned: {search_result[:100]}...")

    # Cleanup
    found_file = _find_issue_path(iss_uniq_id)
    if found_file:
        os.remove(found_file)
        print(f"\nCleanup: Removed {found_file}")

    return iss_uniq_id


def test_short_stage_names():
    """Test that short stage names (inbox, processing, etc.) work."""
    print("\n\n=== Testing Short Stage Names ===")

    issue_name = "short_name_test"
    issue_body = "Testing short stage names"
    iss_uniq_id = create_issue(issue_name, issue_body, ["test"])

    if "Error" in iss_uniq_id:
        print(f"Create failed: {iss_uniq_id}")
        return

    # Test short name "inbox"
    print("\nTesting list_issues('inbox')...")
    result = list_issues("inbox")
    if iss_uniq_id in result:
        print("Verification: Short name 'inbox' works.")

    # Test short name "processing"
    print("\nTesting move_issue with 'processing'...")
    result = move_issue(iss_uniq_id, "processing")
    print(f"Result: {result}")
    if "20_Processing" in result:
        print("Verification: Short name 'processing' works.")

    # Test short name "review"
    print("\nTesting move_issue with 'review'...")
    result = move_issue(iss_uniq_id, "review")
    print(f"Result: {result}")
    if "30_ToReview" in result:
        print("Verification: Short name 'review' works.")

    # Test short name "finished"
    print("\nTesting move_issue with 'finished'...")
    result = move_issue(iss_uniq_id, "finished")
    print(f"Result: {result}")
    if "999_Finished" in result:
        print("Verification: Short name 'finished' works.")

    # Cleanup
    found_file = _find_issue_path(iss_uniq_id)
    if found_file:
        os.remove(found_file)
        print(f"Cleanup: Removed {found_file}")


def test_search_vault():
    """Test search_vault auto-detection of regex vs keyword."""
    print("\n\n=== Testing Search Vault ===")

    # Keyword search
    print("\nTesting keyword search 'test'...")
    result = search_vault("test")
    print(f"Result (first 200 chars): {result[:200] if result else 'No results'}...")

    # Regex search (auto-detected by metacharacters)
    print("\nTesting regex search 'test.*issue'...")
    result = search_vault("test.*issue")
    print(f"Result: {result[:200] if result else 'No results'}...")

    # Invalid regex handling
    print("\nTesting invalid regex '[unclosed'...")
    result = search_vault("[unclosed")
    print(f"Result: {result}")
    if "Invalid regex" in result:
        print("Verification: Invalid regex handled correctly.")


if __name__ == "__main__":
    test_harmonized_workflow()
    test_short_stage_names()
    test_search_vault()
    print("\n\n=== All Tests Completed ===")
