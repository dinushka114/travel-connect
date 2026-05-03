import json
import csv
from chatgpt import draft_email

output_file = "outreach_campaign.csv"

try:
    with open('travel_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["post_id", "author_name", "contact_email", "location", "email_draft"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for post in data:
                email_address = post.get("contact_email", "Not provided")
                
                if email_address != "Not provided":
                    print(f"Generating email for {post['author_name']}...")
                    draft = draft_email(post)
                    
                    if draft:
                        writer.writerow({
                            "post_id": post.get("post_id"),
                            "author_name": post.get("author_name"),
                            "contact_email": email_address,
                            "location": post.get("location"),
                            "email_draft": draft
                        })
                    else:
                        print(f"Failed to generate draft for {post['author_name']}")
                else:
                    print(f"Skipping {post['author_name']} (No contact email found)")
                    
        print(f"\nSuccess! All drafts saved to {output_file}")

except FileNotFoundError:
    print("Error: 'travel_data.json' not found.")