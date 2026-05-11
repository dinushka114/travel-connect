import os
import json
import streamlit as st
import pandas as pd

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from scraper import TravelConnectScraper
from chatgpt import draft_email

st.set_page_config(page_title="AIRPARK Outreach", page_icon="✈️", layout="wide")
st.title("AIRPARK Outreach Pipeline")
st.caption("Scrape Travel Connect leads and draft personalized outreach emails in one click.")

if "posts" not in st.session_state:
    st.session_state.posts = None
if "emails" not in st.session_state:
    st.session_state.emails = None

SOURCE_URL = "https://dinushka114.github.io/travel-connect/"

if st.button("Generate emails", type="primary", use_container_width=True):
    st.session_state.posts = None
    st.session_state.emails = None

    if not os.environ.get("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set. Add it to .streamlit/secrets.toml or your Streamlit Cloud secrets.")
        st.stop()

    with st.spinner("Fetching and parsing posts..."):
        scraper = TravelConnectScraper(SOURCE_URL)
        html = scraper.fetch_page()
        if not html:
            st.error("Failed to fetch the page.")
            st.stop()
        scraper.parse_posts(html)
        st.session_state.posts = scraper.posts_data

    posts = st.session_state.posts
    st.success(f"Scraped {len(posts)} posts.")

    if posts:
        st.subheader("Scraped leads")
        st.dataframe(pd.DataFrame(posts), use_container_width=True)

    targets = [p for p in posts if p.get("contact_email", "Not provided") != "Not provided"]
    rows = []
    if targets:
        progress = st.progress(0.0, text="Drafting emails...")
        for i, post in enumerate(targets, start=1):
            try:
                draft = draft_email(post)
            except Exception as e:
                draft = f"[Error: {e}]"
            rows.append({
                "post_id": post.get("post_id"),
                "author_name": post.get("author_name"),
                "contact_email": post.get("contact_email"),
                "location": post.get("location"),
                "email_draft": draft,
            })
            progress.progress(i / len(targets), text=f"Drafted {i}/{len(targets)}")
        progress.empty()

    st.session_state.emails = rows
    skipped = len(posts) - len(targets)
    st.success(f"Drafted {len(rows)} emails. Skipped {skipped} posts without an email address.")

if st.session_state.posts and not st.session_state.emails:
    st.subheader("Scraped leads")
    posts_df = pd.DataFrame(st.session_state.posts)
    st.dataframe(posts_df, use_container_width=True)

if st.session_state.posts:
    posts_df = pd.DataFrame(st.session_state.posts)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download leads (CSV)",
            data=posts_df.to_csv(index=False).encode("utf-8"),
            file_name="travel_data.csv",
            mime="text/csv",
        )
    with c2:
        st.download_button(
            "Download leads (JSON)",
            data=json.dumps(st.session_state.posts, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name="travel_data.json",
            mime="application/json",
        )

if st.session_state.emails:
    st.subheader("Outreach drafts")
    emails_df = pd.DataFrame(st.session_state.emails)
    st.dataframe(emails_df, use_container_width=True)
    st.download_button(
        "Download outreach campaign (CSV)",
        data=emails_df.to_csv(index=False).encode("utf-8"),
        file_name="outreach_campaign.csv",
        mime="text/csv",
    )

    for row in st.session_state.emails:
        with st.expander(f"{row['author_name']}  —  {row['contact_email']}"):
            st.markdown(row["email_draft"])
