from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import forms
import openai
import re
from resume import models
openai.api_key = ''


class chatgptapi:
    def __init__(self):
        self.responsepattern = r'\[(.*?)\]'
    def gen_response(self,inp):
        messages = [{"role":"user","content":inp}]
        chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages
                )
        reply = chat.choices[0].message.content
        return reply
    def parse_gpt_response(self,response):
        out = re.findall(self.responsepattern,response)
        return out #dtype = list, list of all values within square braces

@login_required
def main_board(request):
    
    user_resume = models.Resume.objects.filter(user=request.user).first()
    context={}
    # Check if the user's resume exists
    if user_resume:
        
        # Check if job roles exist in the database for this user's resume
        existing_roles = user_resume.job_roles.all()

        if existing_roles:
            roles = [role.role for role in existing_roles]  # Extract job roles from the database entries
        else:
            # If roles don't exist, generate using GPT-3
            chat_api = chatgptapi()

            prompt = user_resume.text_content + ". Use this to suggest the top 3 job roles for this user. Reply with the job roles in python list format. Example - [Full stack developer] , [machine learning engineer], [Computer Vision Researcher]: "
            
            # Generate response using the user's resume text
            gpt_response = chat_api.gen_response(prompt)
            
            # Parse the GPT-3 response
            roles = chat_api.parse_gpt_response(gpt_response)
            for role_name in roles:
                models.JobRole.objects.create(resume=user_resume, role=role_name)

            # Save the generated roles to the database

        if request.method == 'POST':
            role_form = forms.JobRoleForm(request.POST)
            if role_form.is_valid():
                role_name = role_form.cleaned_data['role_name']
                
                chat_api = chatgptapi()
                
                
                
                
                # Further process the concatenated_string if needed
                # For demonstration, we're just printing it
                
                chat_api = chatgptapi()
                prompt = user_resume.text_content +'. This is my Resume. Give top 5 skills that I need to learn for this job and I do not already have in my resume: '+role_name+". Strictly Give the skills in the following format, example - [ AWS ] [ React ] [ CSS ] [ Javascipt ] [ Docker ] ."
                
                gpt_response = chat_api.gen_response(prompt)
                
            # Parse the GPT-3 response
                
                skills = chat_api.parse_gpt_response(gpt_response)
                for i in range(len(skills)):
                    skills[i]=skills[i].strip()
                context['skills']=skills
                # Return a success message or redirect the user if needed
                
        else:
            role_form = forms.JobRoleForm()
        context['roles']=roles
        context['role_form']=role_form
        
        return render(request, 'dashboard/dashboard.html', context)
    


    else:

        # Handle case if the user has not uploaded a resume yet
        return render(request, 'dashboard/dashboard.html', {'message': "Please upload a resume first."})
    
@login_required
def enhance(request):
    user_resume = models.Resume.objects.filter(user=request.user).first()
    if user_resume:
        if request.method == "POST":
            form = forms.TextInputForm(request.POST)
            if form.is_valid():
                entered_text = form.cleaned_data['Section']
                role=form.cleaned_data['role_company']
                chat_api = chatgptapi()
                if len(role)>0:
                    prompt=user_resume.text_content + "Taylor or Reformat the following section of my resume for the following role at the company, use strong action verbs, mention skills and make my resume impressionable to a recruitor hiring for this role, Don't Enter Fake Data that you don't know, just highlight the skills related to the role : "+ entered_text+" "+role 
                else:
                    prompt = user_resume.text_content + "Taylor or Reformat the following section of my resume, use strong action verbs, mention skills and make my resume impressionable to a recruitor : "+ entered_text 
                
                # Generate response using the user's resume text
                gpt_response = chat_api.gen_response(prompt)
                # Here, you can process the text as needed. For now, we'll just redirect.
                return render(request, 'dashboard/enhance.html', {'form': form, 'gpt': gpt_response })   # Redirect to some other view
        else:
            form = forms.TextInputForm()

        return render(request, 'dashboard/enhance.html', {'form': form})
    else:
        return render(request, 'dashboard/enhance.html', {'message': "Please upload a resume first."})
@login_required
def ask(request):
    user_resume = models.Resume.objects.filter(user=request.user).first()
    if user_resume:
        if request.method == 'POST':
            text_value = request.POST.get('ask-me-anything', '')
            
            
            
            if text_value:
                chat_api = chatgptapi()
                prompt=user_resume.text_content+". "+text_value.strip()
                gpt_response = chat_api.gen_response(prompt)
                return render(request, 'dashboard/ask.html', {'gpt': gpt_response}) 
            
                # This will print the value entered in the text input


        # ... rest of the view logic
        return render(request, 'dashboard/ask.html')
    else:
        return render(request, 'dashboard/enhance.html', {'message': "Please upload a resume first."})

class courses_split:
    def __init__(self):
        pass
    def get_separate(self,data):
        entry = data[0:data.find("Intermediate Courses")] 
        intermediate = data[data.find("Intermediate Courses"):data.find("Advanced Courses")]
        adv = data[data.find("Advanced Courses"):]
        return entry,intermediate,adv

@login_required
def courses(request,skill_name):
    user_resume = models.Resume.objects.filter(user=request.user).first()
    print(skill_name)
    if user_resume:

        chat_api = chatgptapi()
        prompt="List 2 Entry Level Courses, 2 Intermediate and 2 Advanced Online Course names with their instructors or company for the following skill : "+skill_name
        gpt_response = chat_api.gen_response(prompt)
        c_s=courses_split()
        entry,inter,adv=c_s.get_separate(gpt_response)

        return render(request, 'dashboard/courses.html', {'course': skill_name, 'entry': entry,'inter':inter,'adv':adv}) 
            
                # This will print the value entered in the text input


        
    else:
        return render(request, 'dashboard/dashboard', {'message': "Please upload a resume first."})
    

from django.shortcuts import render, redirect
class match_split:
    def __init__(self):
        pass
    def get_separate(self,data):
        entry = data[0:data.find("Weaknesses")] 
        adv = data[data.find("Weaknesses"):]
        return entry,adv

def job_description_view(request):
    user_resume = models.Resume.objects.filter(user=request.user).first()
    if user_resume:
        if request.method == "POST":
            form = forms.JobDescriptionForm(request.POST)
            if form.is_valid():
                # Extract job description and perform your operations here
                job_description = form.cleaned_data['description']
                chat_api = chatgptapi()
                prompt=user_resume.text_content+" "+"Analyse my resume and give strengths and weaknesses with regards to the following job description in 100 words. "+job_description+"."
                gpt_response = chat_api.gen_response(prompt)
                m_s=match_split()
                st,wk=m_s.get_separate(gpt_response)
                # ... perform some operations on the job description ...
                
                form = forms.JobDescriptionForm()
                # Redirect or render a template with results or a success message
                return render(request, 'dashboard/match.html', {'form': form, 'st': st,'wk':wk})  # assuming you have a URL named 'success_page'
        else:
            form = forms.JobDescriptionForm()
        return render(request, 'dashboard/match.html', {'form': form})
    else:
        return render(request, 'dashboard/dashboard', {'message': "Please upload a resume first."})
    
