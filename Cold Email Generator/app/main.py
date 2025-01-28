import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import send_email
import re

# Set Streamlit page configuration (MUST be first Streamlit command)
st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")


# Clean up text to remove quoted content from previous emails
def clean_text(text):
    # Regular expression to remove quoted text (anything starting with 'On' or 'From' etc.)
    cleaned_text = re.sub(r"(^|\n)(On .* wrote:|From .* on .*|.*\n)", "", text)
    return cleaned_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold EMail Generator and Sender")

    # Input URL
    url_input = st.text_input("Enter a URL:", value="")

    # User details input
    st.subheader("Enter Your Details")
    user_name = st.text_input("Full Name:", "")
    user_email = st.text_input("Your Email:", "")
    phone_number = st.text_input("Phone Number:", "")
    linkedin_link = st.text_input("LinkedIn URL:", "")
    github_link = st.text_input("GitHub URL:", "")

    # Initialize session state for email generation
    if "email" not in st.session_state:
        st.session_state["email"] = None

    if "recipient_email" not in st.session_state:
        st.session_state["recipient_email"] = None

    # Submit button to generate email
    if st.button("Generate Email"):
        if not url_input.strip():
            st.error("Please enter a valid URL!")
            return

        try:
            # Load and clean text from the URL
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            # Load portfolio and extract jobs
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            # Generate an email for the first job (if available)
            if jobs:
                first_job = jobs[0]  # Get the first job description
                skills = first_job.get('skills', [])
                links = portfolio.query_links(skills)

                # Generate the email for the first job
                email = llm.write_mail(
                    first_job, links, user_name, user_email, linkedin_link, github_link
                )
                email += f"\nPhone: {phone_number}"  # Add phone number to the email
                st.session_state["email"] = email
                st.session_state["recipient_email"] = first_job.get(
                    'email', 'recipient@company.com'
                )  # Extract recruiter email

            else:
                st.error("No jobs found in the provided URL.")
                return

        except Exception as e:
            st.error(f"An Error Occurred: {e}")
            return

    # Display and edit the generated email
    if st.session_state["email"]:
        st.subheader("Generated Email")
        email_editable = st.text_area(
            "You can also edit the email below before sending:",
            value=st.session_state["email"],  # Show the full email text
            height=300,
        )

        # Save the updated email content back to session state
        st.session_state["email"] = email_editable

        # Save as TXT button
        if st.button("💾 Save as TXT"):
            file_name = "generated_email.txt"
            with open(file_name, "w") as file:
                file.write(st.session_state["email"])
            st.download_button(
                label="Download Email as TXT",
                data=st.session_state["email"],
                file_name=file_name,
                mime="text/plain",
            )

        # Input recruiter's email for sending
        recipient_email = st.text_input(
            "Recruiter's Email:", value=st.session_state["recipient_email"]
        )

        # Upload resume at the end
        st.subheader("Upload Your Resume (Optional)")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or Word):", type=["pdf", "doc", "docx"]
        )

        # Send Email button
        if st.button("Send Email"):
            if not recipient_email.strip():
                st.error("Please enter the recipient's email!")
                return

            try:
                # Attach the resume if uploaded
                attachments = []
                if uploaded_file:
                    resume_data = uploaded_file.read()
                    resume_name = uploaded_file.name
                    attachments.append((resume_name, resume_data))

                # Use the full edited content of the email
                send_email(
                    sender_email=user_email,
                    recipient_email=recipient_email,
                    subject="Job Application",
                    body=st.session_state["email"],  # Send full email content
                    attachments=attachments,  # Attach the uploaded resume if present
                )
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    # Instantiate classes
    chain = Chain()
    portfolio = Portfolio()

    # Run the app
    create_streamlit_app(chain, portfolio, clean_text)
