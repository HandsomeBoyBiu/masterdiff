#!/usr/bin/python3
from git import Repo
import re
import argparse

suffix_whitelist = (".c", ".cpp", ".cxx")           # TODO

def get_sorted_commits(repo_path):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits("main", reverse=True)) # TODO: Can we autodetect the last commit?
    commit_list = []
    for commit in commits:
        commit_list.append({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
        })
    return commit_list

def parse_diff(diff):
    parsed_diff = []
    for diff_item in diff:
        diff_info = {
            "file": diff_item.b_path or diff_item.a_path,
            "change_type": diff_item.change_type,
            "additions": 0,
            "deletions": 0,
            "modified_lines": []
        }
        
        if diff_item.diff:
            diff_text = diff_item.diff.decode("utf-8", errors="ignore")
            diff_lines = diff_text.splitlines()
            
            old_line_num = None
            new_line_num = None

            for line in diff_lines:
                if line.startswith("@@"):
                    # @@ -old_row,old_col +new_row,new_col @@
                    match = re.search(r"@@ -(\d+),?\d* \+(\d+),?\d* @@", line)
                    if match:
                        old_line_num = int(match.group(1))  
                        new_line_num = int(match.group(2))  
                elif line.startswith("+") and not line.startswith("+++"):
                    diff_info["additions"] += 1
                    diff_info["modified_lines"].append({"line_num": new_line_num, "content": line[1:].strip()})
                    new_line_num += 1
                elif line.startswith("-") and not line.startswith("---"):
                    diff_info["deletions"] += 1
                    diff_info["modified_lines"].append({"line_num": old_line_num, "content": line[1:].strip()})
                    old_line_num += 1
        
        parsed_diff.append(diff_info)
    return parsed_diff

def get_diff_between_commits(repo_path, commit1, commit2):
    repo = Repo(repo_path)
    commit1_obj = repo.commit(commit1)
    commit2_obj = repo.commit(commit2)

    diff = commit2_obj.diff(commit1_obj, create_patch=True) 
    return parse_diff(diff)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='masterdiff is a tool that can help you analyze and export the files changed in each commit in the git repository')
    parser.add_argument('--repo', type=str, help='Your repoitory path', required=True)      
    parser.add_argument('--output', type=str, help='Output directory path, default: ./', default='./')
    parser.add_argument('--last', type=int, help='Number of recent changes to extract, default: 5', default=5)

    repo_path = parser.parse_args().repo
    output_path = parser.parse_args().output
    last = parser.parse_args().last
    
    commits = get_sorted_commits(repo_path)
    if not commits or len(commits) < 2:
        print("Not enough commits to compare.")
    else:
        source_code_changes = []

        for i in range(1, len(commits)):
            current_commit = commits[i]
            previous_commit = commits[i - 1]
            current_change = dict()
            
            diff = get_diff_between_commits(repo_path, previous_commit["hash"], current_commit["hash"])
            current_change["current_commit"] = current_commit["hash"]
            current_change["previous_commit"] = previous_commit["hash"]
            current_change["date"] = current_commit["date"]
            current_change["all_changes"] = []

            for file_diff in diff:
                file_change = dict()
                file_name = file_diff["file"][file_diff["file"].rfind("/") + 1:]
                changed_lines = []

                if file_name.endswith(suffix_whitelist):
                    for line in file_diff["modified_lines"]:
                        changed_lines.append(line["line_num"])
                
                if len(changed_lines) > 0:
                    file_change["file"] = file_name
                    file_change["changed_lines"] = list(changed_lines)
                    current_change["all_changes"].append(file_change)

            if len(current_change["all_changes"]) > 0:
                source_code_changes.append(current_change)

        last_changes = source_code_changes[-last:]
        change_pool = set()

        for change in last_changes:
            for idx in range(len(change["all_changes"])):
                file_name = change["current_commit"][:7] + "_" + change["previous_commit"][:7] + "_" + str(idx) + "_" + change["all_changes"][idx]["file"] + ".tgt"
                with open(output_path + file_name, "w") as f:
                    for line in change["all_changes"][idx]["changed_lines"]:
                        f.write(change["all_changes"][idx]["file"] + ":" + str(line) + "\n")
                        change_pool.add(change["all_changes"][idx]["file"] + ":" + str(line))

        with open(output_path + "targets.txt", "w") as f:
            for change in change_pool:
                f.write(change + "\n")
        
