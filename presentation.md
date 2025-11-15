# System Information Generator Presentation

---

## Slide 1: Introduction
- Overview of the System Information Generator project
- Objectives of the presentation

---

## Slide 2: Team Members
- List of team members and their roles
- Belza - Project Lead
- Constantino - Frontend Developer
- Sabangan - Backend Developer
- Santiago - Database Administrator
- Silvestre - DevOps Engineer

---

## Slide 3: Belza's Contributions
- Project Management
- Team Coordination
- Milestone Tracking

---

## Slide 4: Key Achievements by Belza
- Successful Initialization of the Project
- Setting up Project Guidelines

---

## Slide 5: Constantino's Contributions
- UI Design and Development
- User Experience Enhancements

---

## Slide 6: UI Design Overview
![UI Design](design_image_link)  
- Color Scheme: Blue and White  
- Components used: Buttons, Forms, Navigation

---

## Slide 7: Code Snippet by Constantino
```javascript
// Sample JavaScript code for button functionality
const button = document.getElementById('submit');
button.addEventListener('click', function() {
    alert('Button Clicked!');
});
```

---

## Slide 8: Sabangan's Contributions
- Backend Development
- API Integrations

---

## Slide 9: API Architecture
| Method | Endpoint           | Description                     |
|--------|-------------------|---------------------------------|
| GET    | /api/info         | Retrieve System Information      |
| POST   | /api/generate     | Generate System Information      |

---

## Slide 10: Code Implementation
```python
# Sample Python code for API endpoint
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/info', methods=['GET'])
def get_info():
    return jsonify({'info': 'System Info Data'})
```

---

## Slide 11: Challenges Faced
- Handling Large Data Sets
- Ensuring API Security

---

## Slide 12: Santiago's Contributions
- Database Management
- Data Modeling

---

## Slide 13: Database Schema
![DB Schema](schema_image_link)  
- Tables: Users, Reports, Logs  
- Relationships: One-to-Many, Many-to-Many

---

## Slide 14: Future Work
- Optimizing Database Queries
- Planning for Scaling
- Upcoming Feature Additions

---