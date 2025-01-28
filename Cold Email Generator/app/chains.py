import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: role, experience, skills, description, and email.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links, user_name, user_email, linkedin_link, github_link):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            Draft a cold email applying for the job mentioned above. The email should clearly state interest in the role, describe relevant skills and experiences, and explain how these align with the company's requirements. Include any significant achievements, certifications, or links to a portfolio, if applicable: {link_list}. Use the user's personal details provided below:

            - Full Name: {user_name}
            - Email: {user_email}
            - LinkedIn: {linkedin_link}
            - GitHub: {github_link}

            The tone should be professional, confident, and enthusiastic.  
            Ensure proper formatting with appropriate line breaks between paragraphs to avoid text stretching unnecessarily.

            ### EMAIL (NO PREAMBLE):

            Dear [Recipient's Name],

            I am excited to apply for the [Job Title] role at [Company Name].  
            [Start with a brief introduction and a clear statement of interest in the position].

            [Provide a detailed overview of relevant experience and skills tailored to the job description].  
            My background in [specific expertise/field] 
            has allowed me to [highlight a key achievement or skill relevant to the role].

            [Mention certifications, achievements, or include portfolio links from {link_list} to demonstrate fit].  
            I am confident that my expertise in [specific areas] will make a meaningful impact on your team  
            and contribute to [company's goals relevant to the role].

            I would greatly appreciate the opportunity to discuss how I can bring value to [Company Name].  
            Thank you for considering my application.

            Best regards,  
            {user_name}  
            {user_email}  
            LinkedIn: {linkedin_link}  
            GitHub: {github_link}
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job),
            "link_list": links,
            "user_name": user_name,
            "user_email": user_email,
            "linkedin_link": linkedin_link,
            "github_link": github_link
        })
        return res.content
