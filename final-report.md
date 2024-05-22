# Integration: Phase2
**Team:** Liza Mozolyuk, Yusef lname, Matt lname

## SQL Table Diagram
<img width="1252" alt="Screen Shot 2023-05-04 at 12 55 51 PM" src="https://user-images.githubusercontent.com/35519843/236273632-ebf9edcc-e7ed-44c4-9a32-8750c6148c74.png">


### Normal Forms
We believe that our databse is in 3NF. Each table has a primary key that uniquely identifies each row. There are no repeating groups within the tables. There are no transitive dependencies between non-primary key columns within each table. Our databse is not in BCNF because in some of our tables (ex. `user`) we have multiple fields that could candidate keys such as the username and user_id.

## Visual Overview

## Index Page
<img width="1352" alt="Screen Shot 2023-05-04 at 3 44 28 PM" src="https://user-images.githubusercontent.com/35519843/236321816-ed3c2ebb-0969-413e-b31d-a369d9e4b029.png">

## Login
<img width="1340" alt="Screen Shot 2023-05-04 at 3 44 37 PM" src="https://user-images.githubusercontent.com/35519843/236321859-a5ad857d-1224-4ba9-ad24-5ec8a5d4ae41.png">

## Personal Information


## Application features 
- application home page
<img width="958" alt="Screenshot 2023-05-04 230215" src="https://user-images.githubusercontent.com/112405996/236372052-2d5ab4ce-c319-4d41-8edf-ef661bb245a5.png">
- application form page (buttons to submit data and edit previously submitted data)
<img width="499" alt="image" src="https://user-images.githubusercontent.com/112405996/236372427-947d051f-7c09-4ca6-9dd4-52bb1fa0e767.png">
- applicant status page (changes depending on status of application and whether they have been reject or admitted, in this case they've been admitted)
<img width="956" alt="image" src="https://user-images.githubusercontent.com/112405996/236376372-79ecba63-4bf7-4f96-ab85-b4a9246112e6.png">
- admission payment page (once applicant accepts admission)
<img width="960" alt="image" src="https://user-images.githubusercontent.com/112405996/236376494-f9ad3682-8ed0-4fc5-afbf-4fc88dfee54c.png">
- recommendation letter webpage (which is reached after a webpage where the user inputs an email and it checks if a recommendation letter has been requested)
<img width="959" alt="image" src="https://user-images.githubusercontent.com/112405996/236376822-32803124-f051-4eae-b945-c0024bd83584.png">
- review form page (only for cac and faculty reviewers)
<img width="938" alt="image" src="https://user-images.githubusercontent.com/112405996/236376912-97ea4dce-46bc-4c07-a197-a3aa13bd2104.png">
- page for gs and sysadmin that displays all applicant data
<img width="944" alt="image" src="https://user-images.githubusercontent.com/112405996/236377035-ad44d252-7a62-4097-be6d-3e95f8bb87ac.png">
- page for gs and sysadmin that displays all reviews
<img width="958" alt="image" src="https://user-images.githubusercontent.com/112405996/236377271-88d9b44f-355b-40e4-b5df-8e0e3bc2734e.png">
- page to view applicants, where they can accept them, making them students (faculty reviewers dont have access to the buttons in this)
<img width="959" alt="image" src="https://user-images.githubusercontent.com/112405996/236377933-6558ffc9-ca16-4f6c-b34c-a6e1713cfe7b.png">
- applicant statistics page
<img width="941" alt="image" src="https://user-images.githubusercontent.com/112405996/236378065-868f45bf-8372-46f4-a62a-04d557f19a73.png">

## Registration features
**registration page:**
<img width="1440" alt="Screenshot 2023-05-04 at 3 46 58 PM" src="https://user-images.githubusercontent.com/112406436/236403946-31d0d691-ce68-44d0-87f1-323fb588993c.png">

**course catalog/list:**
<img width="1440" alt="Screenshot 2023-05-05 at 4 01 03 AM" src="https://user-images.githubusercontent.com/112406436/236405922-5b53e9af-0911-4e3e-8a96-b929d3831bed.png">

**course pages individual:**
<img width="1440" alt="Screenshot 2023-05-05 at 4 02 16 AM" src="https://user-images.githubusercontent.com/112406436/236406129-1d4e28bb-f0b3-45ee-a77e-953233f2ed28.png">



**assign grades:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 51 30 AM" src="https://user-images.githubusercontent.com/112406436/236404070-f58eceac-8642-4008-a949-c58458ea8edd.png">

**assign professor:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 52 08 AM" src="https://user-images.githubusercontent.com/112406436/236404180-cc0695f4-65d6-44f0-a6c0-ad49fdb1ac63.png">

**transcript:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 53 36 AM" src="https://user-images.githubusercontent.com/112406436/236404479-287853bd-5969-44d4-9edf-e3efe22fe2b9.png">

**course list:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 54 02 AM" src="https://user-images.githubusercontent.com/112406436/236404660-2679f73a-6e4e-4ca9-8ff3-c9c4ae198bb4.png">

**professor list:**

<img width="1440" alt="Screenshot 2023-05-05 at 3 55 20 AM" src="https://user-images.githubusercontent.com/112406436/236404774-e0f2b531-2625-4b86-91a5-7b4063afae00.png">

**current courses:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 56 32 AM" src="https://user-images.githubusercontent.com/112406436/236405087-d725ff9e-eb37-42ae-b29c-f5423ba661a2.png">
**
view classmates:**
<img width="1440" alt="Screenshot 2023-05-05 at 3 58 15 AM" src="https://user-images.githubusercontent.com/112406436/236405376-5f7a7a34-4b72-40ed-845e-61f80888e9d3.png">

**message classmates**
<img width="1440" alt="Screenshot 2023-05-05 at 3 58 43 AM" src="https://user-images.githubusercontent.com/112406436/236405467-4f27f9dc-5d1f-45a6-af7b-73b9105f945a.png">

## Advising features
- veiw advisees
<img width="1342" alt="Screen Shot 2023-05-04 at 3 45 26 PM" src="https://user-images.githubusercontent.com/35519843/236322290-66308c1c-74e1-4d2f-9dbe-cb3bba6a4ea1.png">
-view al students
<img width="1340" alt="Screen Shot 2023-05-04 at 3 47 08 PM" src="https://user-images.githubusercontent.com/35519843/236322438-b1ba5015-8288-44ce-a559-814952a57abc.png">




## Design Justification
- Navigation bar: Allows the user to return to their "home" page at all times, access their personal information page, and quickly log out. 
- We split some routes/modules (like user management, transcripts, and student management) into their own files/Blueprints to increase readability of our code, maintain consistent URL structures, more easily identify errors, and collaborate on code better.
- In an effort to reuse as much code as possible, we created a base HTML template that was included on (almost) every other template. We also tried to use macros wherever possible to save modularize our HTML as much as possible.
    - This decision also affected how user roles with more permissions (such as grad secretaries and sysadmins) access different functiions of the system; rather than having one list of all users with specific functions for each user based on the user type, they access different index pages for different functions (i.e. alumni list vs. student list vs. user list).
- We used Bootstrap as our styling framework so that we could spend the majority of our time developing functionality and not as much defining custom styling to make our advising system user-friendly. We also used DataTables to improve our tables (to allow for searching/pagination/sorting).
- We added client-side validation to forms wherever possible so as to give users more descriptive feedback on their inputs before submitting the form data to the back-end. (Validation, often more in-depth, was also done on the back-end.)
- The applications page was mainly just the front of the website and most additions were made for the applicant user type, with some being added to existing faculty and gs users
- It was assumed anyone could access the recommendation letter page as long as they had the email that a letter had been requested of. It was also assumed that the transcript for applicants does not affect them as students, and that the transcript for applicants is simply just marked as received or not received in the system.
- We had to adjust the course table from reg as it stored prereqs in a way that vialoated normal form, so we created a prereq table for a many to many relationship
- We had to make some considerations about account type, we do not allow a user to have multiple roles. we believe this may not be the most efficent method but it makes leakage and edge case errors less possible. with the time we had, we believe this was neccesary.

## Aditional Features

## Alumni Chatroom
- The alumni chatroom enables graduated students to chat to eachother. The messages are stored through the databse which lets each user logged on the chat to be able to see what is happening in conversation.
<img width="1330" alt="Screen Shot 2023-05-03 at 9 53 17 PM" src="https://user-images.githubusercontent.com/35519843/236092405-91e6595a-789f-40b2-bff6-4603e1dd7b96.png">

## Student-Student and Professor-Student Messaging
- Students can click view classmates to see their classmates, the student can then click the message button next to all of their classmates to message them indivudally, which they will receive in thre inbox.  A professor can also see a list of their students and message them as well.
<img width="1440" alt="Screenshot 2023-05-05 at 4 05 20 AM" src="https://user-images.githubusercontent.com/112406436/236406633-8bed7d9b-1bbd-4594-9497-8650e7e259b1.png">

<img width="1440" alt="Screenshot 2023-05-05 at 4 06 23 AM" src="https://user-images.githubusercontent.com/112406436/236406848-91b8b322-1e6a-415f-a78c-90c48fee1486.png">

## Rate My professor/courses
- Students can look at their previous professors/courses from their home screen. They can rate each of them out of 5 and leave a comment.
- The course list and professr list now have buttons that show the professors/courses ratings
<img width="1440" alt="Screenshot 2023-05-05 at 3 42 37 AM" src="https://user-images.githubusercontent.com/112406436/236402477-b4178bdd-1a44-4842-ae27-39e1eb2d4144.png">






## Work breakdown
-Liza:
    -[x] Alumni chatroom feture and style for template 
    -[x] ER Diagram
    -[x] Added faculty table and made checks for authoriztion
    -[x] user home pages for the faculty, sysadmin, and gs
    -[x] navbar design for minecraft theme
    -[x] dummy data
    -[x] queries for gs with respect to ADS

-Matt:
    -[x] Rate my professor and Rate my course functionality
    -[x] classmates page, Student Messaging system and professor student list, and messaging system
    -[x] Professor list/course List that shows ratings/comments for each and average rating
    -[x] worked on Student home page
    -[x] Integreated registration into lizas general pages
    -[x] Inbox for messages from classmates and professor
    
-Yusef:
   -[x] All aspects of applications (application page, reviewers and so on)
   -[x] Ensured checks for all functions (and restrictions based on type of faculty)
   -[x] Background image, button, and some of the text styles for all webpages 
   -[x] worked on index home page
   -[x] Integreated application page into lizas general pages
   -[x] Queries and reports for APPS


