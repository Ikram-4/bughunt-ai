# 🎯 BugHunter Pro Report — lovable.dev
**Date:** 2026-03-08 11:19:41
**Output:** hunt_lovable.dev_20260308_094912/

---

## 📊 Recon Statistics

| Phase | Count |
|-------|-------|
| Passive Subdomains | 78 |
| Resolved Subdomains | 67 |
| Live Web Hosts | 0 |
| Total URLs | 174505 |
| JS Files Analyzed | 11 |
| Source Maps Found | 0 |
| Secrets Found | 22 |
| GraphQL Endpoints | 0 |
| API Paths Discovered | 0 |

---

## 🔥 HIGH PRIORITY FINDINGS

### 🔴 Exposed Admin Panels
```
None found
```

### 🔴 Default Credentials
```
None found
```

### 🔴 High/Critical CVEs
```
None found
```

### 🟠 Source Maps (Unminified Source Code Exposed)
```
None found
```

### 🟠 Subdomain Takeovers
```
[ * ] Fingerprints not found; saving them to "/home/ikram/subzy/fingerprints.json"
```

### 🟠 CORS Misconfigurations
```
None found
```

### 🔴 CORS Standalone Testing
```
None found
```

### 🔴 CNAME Takeover Candidates
```
cms.lovable.dev [[35mCNAME[0m] [[32mlovable.netlifyglobalcdn.com[0m]
```

### 🔴 Sensitive Files Exposed
```
https://lovable.dev/robots.txt
https://lovable.dev/sitemap.xml
http://lovable.dev/robots.txt
http://lovable.dev/sitemap.xml
```

### 🔴 CRLF Injection
```
None found
```

### 🔴 Open Redirects Confirmed
```
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: apiKey
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: appName
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: authType
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: redirectUrl
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: v
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: eventId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: providerId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail | param: scopes
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: apiKey
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: appName
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: authType
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: redirectUrl
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: v
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: eventId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: providerId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail | param: scopes
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: apiKey
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: appName
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: authType
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: redirectUrl
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: v
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: eventId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: providerId
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail | param: scopes
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: apiKey
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: appName
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: authType
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: redirectUrl
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: v
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail | param: eventId
```

### 🟠 Host Header Injection
```
None found
```

### 🔴 Dalfox XSS Findings
```
[POC][R][GET][inJS-none(2)] http://lovable.dev/_next;alert.apply(null,[1]);/image?=&q=75&url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080
[POC][R][GET][inJS-none(2)] http://lovable.dev/_next;frames[/al/.source+/ert/.source](/XSS/.source);/image?=&q=75&url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080
[POC][R][GET][inJS-none(2)] http://lovable.dev/_nextalert(1)/image?=&q=75&url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080
```

### 🟠 Secrets in JavaScript
```
None found
```

### � GraphQL Introspection
```
None found
```

### 🔴 GraphQL Schema Types
```
None found
```

### 🟠 API Endpoints Discovered
```
None found
```

### 🟠 HTTP Method Fuzzing Hits
```
None found
```

### �🟡 SSRF-Prone Parameters
```
200      GET        2l     1386w    65820c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal
200      GET        2l     1386w    65820c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Fsettings
200      GET        2l     1386w    65824c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Fdashboard
200      GET        2l     1386w    65830c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.bak
200      GET        2l     1386w    65834c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.aspx
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.asp
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.jsp
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.old
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.php
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.txt
200      GET        2l     1386w    65840c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.json
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=2048&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fwired-logo.png&w=384&q=75
https://api.lovable.dev/projects/community?limit=16&view=featured
https://api.lovable.dev/projects/community?limit=32&view=featured
https://api.lovable.dev/users/26LOkZDiijS73yHSpEg7YftfCQ02/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/4wm6dKRVE7gyvnhRWt8HiOmmnwh1/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/52XY5dDq6ndoVAu59uGUklDj49j2/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/8zjo3uCsMKZ2SpGmgI4xMKALDfv2/projects?limit=100&sort_by=updated_at&order=desc
```

### 🟡 Open Redirect Parameters
```
200      GET        2l     1386w    65820c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal
200      GET        2l     1386w    65820c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Fsettings
200      GET        2l     1386w    65824c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Fdashboard
200      GET        2l     1386w    65830c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.bak
200      GET        2l     1386w    65834c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.aspx
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.asp
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.jsp
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.old
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.php
200      GET        2l     1386w    65836c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.txt
200      GET        2l     1386w    65840c https://lovable.dev/login?redirect=https%3A%2F%2Flovable.dev%2Finternal.json
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=2048&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fwired-logo.png&w=384&q=75
https://api.lovable.dev/users/26LOkZDiijS73yHSpEg7YftfCQ02/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/4wm6dKRVE7gyvnhRWt8HiOmmnwh1/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/52XY5dDq6ndoVAu59uGUklDj49j2/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/8zjo3uCsMKZ2SpGmgI4xMKALDfv2/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/GZSDUutSZPPX31zCLfgEyYt8Mtx2/projects?limit=100&sort_by=updated_at&order=desc
https://api.lovable.dev/users/Ir8ixzLjdBVxgqzE7C6XDbFy50Z2/projects?limit=100&sort_by=updated_at&order=desc
```

### 🟡 XSS-Prone Parameters
```
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=1080&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fbackground%2Ffooter-background-card.jpg&w=2048&q=75
http://lovable.dev/_next/image?url=%2Fimg%2Fwired-logo.png&w=384&q=75
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dloveable%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BCORE%26campaignid%3D23078175983%26devicetype%3Dc%26gclid%3DCj0KCQiAiqDJBhCXARIsABk2kSm5jvl-GXEFZOAGWYtIg03pFxQ0KBVejT4btR2PbRCDuwlIOImR-QcaAlz0EALw_wcB%26creativeid%3D777017041609%26gad_source%3D1%26gad_campaignid%3D23078175983%26gbraid%3D0AAAAA-iIxGeKlrtfmBrljs4V6xJyj8c4A&v=11.10.0&eventId=3601357276&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_source%3Dloveable_redirect&v=11.10.0&eventId=1323242169&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3D687980%26gad_source%3D1%26gad_campaignid%3D23340049817%26gbraid%3D0AAAABBrDXf2HuzILZ9u66aZieB-A48rZz&v=11.10.0&eventId=2056993377&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dsale62%26gad_source%3D1%26gad_campaignid%3D23012163577%26gbraid%3D0AAAABBR2BMntUDhJrrTyKjESheCaq8P6T%26gclid%3DCj0KCQjwovPGBhDxARIsAFhgkwSU8JPGCDH8x4fwFAQkRU9oJ94xIHIL2ITfT362Am1XLcMoQb1BugoaArBMEALw_wcB&v=11.10.0&eventId=8948914237&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dtinh%26gad_source%3D1%26gad_campaignid%3D23214831772%26gbraid%3D0AAAABB33EJFns48Zi9L3A-ZpkOmcTEaqd%26gclid%3DCj0KCQjw35bIBhDqARIsAGjd-cYVnEWUoy48FoPGJ3QEcptQlsjVQ7xcAGwSgnKwXddqHUNfZsfD4O4aAnHeEALw_wcB&v=11.10.0&eventId=2251674386&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dvantoan%26gad_source%3D1&v=11.10.0&eventId=6738352662&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0032573178&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0221138810&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0626871763&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0679596935&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0721949028&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0862062799&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0990768323&providerId=github.com&scopes=user%3Aemail
```

### 🟡 IDOR-Prone Parameters
```
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%253A%252F%252Flovable.dev%252Fsignup&v=11.10.0&eventId=0270904529&providerId=google.com&scopes=profile%252Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Freferrer%3Dluma&v=11.10.0&eventId=3098279507&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dai%2520website%2520generator%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BAI%2B-%2BBuilder%2B-%2B-%2B-%2BCORE%26campaignid%3D23196544748%26devicetype%3Dc%26gclid%3DCj0KCQiA9OnJBhD-ARIsAPV51xNDzQ-ehJtziG7N00jydiUkzLLulHX2ONr7AvRdRhMI3atCR-uHX0IaAhCxEALw_wcB%26creativeid%3D781134353994%26gad_source%3D1%26gad_campaignid%3D23196544748%26gbraid%3D0AAAAA-iIxGd9UUvWq5qNDppBhbFAuNgEy&v=11.10.0&eventId=1852547095&providerId=github.com&scopes=user%3Aemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dlovable%2520website%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BLT%26campaignid%3D23078175986%26devicetype%3Dc%26gclid%3DCj0KCQjwo63HBhCKARIsAHOHV_UaSPz2yiLVAq5EI8_OpFrf17n8UYNczwUOzcQeJr4nxclTJhdwng0aAk5JEALw_wcB%26creativeid%3D777017047810%26gad_source%3D1%26gad_campaignid%3D23078175986%26gbraid%3D0AAAAA-iIxGch8f3uny97ZQRArL-TviiUt&v=11.10.0&eventId=8826464308&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_feeditemid%3D%26utm_device%3Dc%26utm_term%3Dloveable%26utm_source%3Dgoogle%26utm_medium%3Dppc%26utm_campaign%3DXE%2B-%2BSearch%2B-%2BLovable%2B-%2BCORE%26campaignid%3D23078175983%26devicetype%3Dc%26gclid%3DCj0KCQiAiqDJBhCXARIsABk2kSm5jvl-GXEFZOAGWYtIg03pFxQ0KBVejT4btR2PbRCDuwlIOImR-QcaAlz0EALw_wcB%26creativeid%3D777017041609%26gad_source%3D1%26gad_campaignid%3D23078175983%26gbraid%3D0AAAAA-iIxGeKlrtfmBrljs4V6xJyj8c4A&v=11.10.0&eventId=3601357276&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Futm_source%3Dloveable_redirect&v=11.10.0&eventId=1323242169&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3D687980%26gad_source%3D1%26gad_campaignid%3D23340049817%26gbraid%3D0AAAABBrDXf2HuzILZ9u66aZieB-A48rZz&v=11.10.0&eventId=2056993377&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dsale62%26gad_source%3D1%26gad_campaignid%3D23012163577%26gbraid%3D0AAAABBR2BMntUDhJrrTyKjESheCaq8P6T%26gclid%3DCj0KCQjwovPGBhDxARIsAFhgkwSU8JPGCDH8x4fwFAQkRU9oJ94xIHIL2ITfT362Am1XLcMoQb1BugoaArBMEALw_wcB&v=11.10.0&eventId=8948914237&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dtinh%26gad_source%3D1%26gad_campaignid%3D23214831772%26gbraid%3D0AAAABB33EJFns48Zi9L3A-ZpkOmcTEaqd%26gclid%3DCj0KCQjw35bIBhDqARIsAGjd-cYVnEWUoy48FoPGJ3QEcptQlsjVQ7xcAGwSgnKwXddqHUNfZsfD4O4aAnHeEALw_wcB&v=11.10.0&eventId=2251674386&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F%3Fvia%3Dvantoan%26gad_source%3D1&v=11.10.0&eventId=6738352662&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0032573178&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0221138810&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0626871763&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0679596935&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0721949028&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0862062799&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=0990768323&providerId=github.com&scopes=user%3Aemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=1028806178&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=1080335436&providerId=google.com&scopes=profile%2Cemail
https://auth.lovable.dev/__/auth/handler?apiKey=AIzaSyBQNjlw9Vp4tP4VVeANzyPJnqbG2wLbYPw&appName=%5BDEFAULT%5D&authType=signInViaPopup&redirectUrl=https%3A%2F%2Flovable.dev%2F&v=11.10.0&eventId=1432359668&providerId=google.com&scopes=profile%2Cemail
```

### 🟡 403 Bypass Successes
```
None found
```

### 🟡 Exposed Files
```
None found
```

### 🔵 Token/Secret Exposures
```
None found
```

### 🔵 Misconfigurations
```
None found
```

---

## 📁 Output File Map

```
hunt_lovable.dev_20260308_094912/
├── subdomains/
│   ├── all_passive.txt        ← All discovered subdomains
│   └── [tool-specific files]
├── dns/
│   ├── resolved.txt           ← DNS-confirmed live subdomains
│   └── dns_details.txt        ← A, CNAME, MX records
├── web/
│   ├── live_urls.txt          ← Live HTTP/S hosts
│   ├── httpx_full.txt         ← Full httpx output + tech stack
│   └── 403_hosts.txt          ← 403 hosts (test bypass)
├── ips/
│   └── open_ports.txt         ← Open ports
├── endpoints/
│   ├── all_urls.txt           ← All discovered URLs
│   ├── linkfinder.txt         ← JS-extracted endpoints
│   ├── jsluice_endpoints.txt  ← AST-level JS endpoints
│   └── js_extracted_endpoints.txt ← Regex endpoint extraction
├── params/
│   ├── ssrf_prone.txt         ← SSRF-prone param URLs
│   ├── redirect_prone.txt     ← Open redirect param URLs
│   ├── injection_prone.txt    ← SQLi/XSS param URLs
│   ├── xss_prone.txt          ← Reflected XSS candidates
│   └── idor_prone.txt         ← IDOR-prone param URLs
├── js/
│   ├── js_urls.txt            ← All JS file URLs
│   ├── files/                 ← Downloaded JS files
│   └── maps/                  ← Downloaded source maps
├── secrets/                   ← All secret findings (JSON)
├── graphql/
│   ├── graphql_endpoints.txt  ← Discovered GraphQL endpoints
│   ├── schema_types.txt       ← Extracted schema types
│   └── introspection_*.json   ← Full introspection dumps
├── api/
│   ├── found_api_paths.txt    ← API base paths found
│   ├── method_allowed.txt     ← HTTP method fuzzing hits
│   └── ffuf_*.json            ← ffuf API fuzzing results
├── screenshots/               ← gowitness/aquatone screenshots
├── vulns/                     ← Nuclei/subzy/CORS/CRLF/XSS results
│   ├── cname_takeovers.txt    ← Dangling CNAME takeover candidates
│   ├── sensitive_files.txt    ← Exposed .git/.env/configs
│   ├── cors_misconfig.txt     ← CORS misconfigurations
│   ├── crlf_injection.txt     ← CRLF injection findings
│   ├── open_redirects.txt     ← Confirmed open redirects
│   ├── host_header_injection.txt ← Host header injection
│   ├── dalfox_xss.txt         ← Reflected XSS findings
│   └── sqlmap_*/              ← SQLMap scan results
└── dorks/
    ├── google_dorks.txt       ← 80+ Google dorks
    └── github_dorks.txt       ← GitHub search dorks
```

---

## ⚡ Manual Attack Checklist

### Immediate Priority (check these first):
- [ ] Test all exposed panels in `vulns/nuclei_panels.txt` with default creds
- [ ] Decompile source maps: `sourcemapper -url <URL.map> -output ./src/`
- [ ] Validate all secrets in `secrets/` — test each API key manually
- [ ] Check `vulns/cname_takeovers.txt` — register dead services for takeover
- [ ] Verify `vulns/sensitive_files.txt` — download exposed .git/config/.env files
- [ ] Confirm CORS findings in `vulns/cors_misconfig.txt` — steal tokens via origin
- [ ] Test CRLF in `vulns/crlf_injection.txt` for cache poisoning / XSS
- [ ] Weaponize open redirects in `vulns/open_redirects.txt` for phishing + OAuth bypass
- [ ] Host header injection in `vulns/host_header_injection.txt` — password reset poisoning

### IDOR Testing:
- [ ] Install Autorize in Burp Suite
- [ ] Create 2 accounts (attacker + victim)
- [ ] Browse as high-priv, Autorize retests with low-priv
- [ ] Test all URLs in `endpoints/all_urls.txt` with numeric IDs

### SSRF Testing:
- [ ] Set up: `interactsh-client -v` (note your callback URL)
- [ ] Test all URLs in `params/ssrf_prone.txt`
- [ ] Payload: `http://169.254.169.254/latest/meta-data/` (AWS metadata)

### XSS Testing:
- [ ] Run: `cat endpoints/all_urls.txt | kxss` (reflected XSS finder)
- [ ] Run: `dalfox file endpoints/all_urls.txt --skip-bav`
- [ ] Blind XSS in profile fields with XSS Hunter payload

### Auth Testing:
- [ ] Test JWT: decode + try algorithm=none
- [ ] Password reset: inject `Host: attacker.com` header
- [ ] OAuth: test missing state param, redirect_uri bypass

### GraphQL Testing:
- [ ] If introspection enabled: dump full schema with InQL / graphql-voyager
- [ ] Test batch queries: `[{"query":"..."},{"query":"..."}]`
- [ ] Test query depth attacks (nested queries for DoS)
- [ ] Bypass disabled introspection: try `__type`, `__schema` individually
- [ ] Test for IDOR via GraphQL: `query { user(id: 1) { email } }`
- [ ] Check mutations for privilege escalation

### API Fuzzing:
- [ ] Test all endpoints in `api/found_api_paths.txt` with Burp
- [ ] Try PUT/DELETE on all found paths
- [ ] Test version rollback: /api/v1/ vs /api/v2/ for removed features
- [ ] Check `api/method_allowed.txt` for dangerous method access

### SQLi:
- [ ] Run: `sqlmap -l endpoints/injection_prone.txt --level 5 --batch`

*Generated by BugHunter Pro v4.0*
