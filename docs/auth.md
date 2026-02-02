Authentication and Authorization 
---
Sign Up
- Standard Username and Password Signup
- Password protected using bcrypt
- Option for Google Oauth
- User must login after signup
Login
- Standard Username and Password Login
- Option for Google Oauth
How everything works under the hood 🍪
- Cookies are used in order to persist a users session.
- When logging in user is assigned a access and refresh token which is then stored in the broswer as a cookie for a time of 15 minutes and 14 days respectivley. 
- The same logic is applied when logging in with Google
- The refresh token is stored within a database and if not validated the using is logged out.
- In the case a user makes a request for their information the access token is used however since it expires every 15 minutes in the cases where the token is expired a checkin with  the refresh token is required.
- Everytime the refresh is called a new one is generated and the old one is delted this is too prevent bad actors from having access for too long in the case they do get the refresh token.
