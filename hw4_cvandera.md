Homework 4 Feedback
===================

Commit graded: 443d44136b4154706368f03410966d1231f80da4

### Committing your work (10/10)
  * Good job!

### Specification fulfillment (19/20)
  * **-1** The user data listed on each profile is for the logged in user, rather than the user whose profile is being viewed. 

### Validation (15/20)
  * **-5** You do not check if request parameters are empty strings in your application.

### Routing and configuration (10/10)
  * **-0** Regex strings should end with '$' if you want to designate that as the end of the url. For example, `r'^/' will match with *every* URL even if you don't intend that to be the case. We will begin to take points off for this in future assignments.

### Coverage of technologies (39/40)
  * **-1** When you know there will only be one object (like user profile), you should use the `get` query rather than the `filter` query. See [the associated Django documentation page](https://docs.djangoproject.com/en/1.7/topics/db/queries/#retrieving-a-single-object-with-get) for more info.
  * **-0** Deleting an item should be implemented with a POST request since GET requests are not expected to change server state. We will begin to take off points for this in future assignments.

### Design (0/0)
  * **-0** Perhaps it would be better if you added some sort of persistent navigation bar with common pages. Currently, I can't see my own profile unless I post something.

### Additional comments

---

#### Total score: 93

Late days used: 0

---

Graded by: Divya (dmouli@andrew.cmu.edu)

To view this file with formatting, visit the following page: https://github.com/CMU-Web-Application-Development/cvandera/blob/grades/hw4_cvandera.md
