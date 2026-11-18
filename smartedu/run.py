import os
import sys
from app import app, db
from seed_data import seed_database

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()

    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"       SmartEdu Web Application Launching")
    print(f"=======================================================")
    print(f"Server URL: http://127.0.0.1:{port}")
    print(f"\nQuick Demo Roles:")
    print(f"  • Student: alex_student  / student123")
    print(f"  • Faculty: sarah_faculty / faculty123")
    print(f"  • Admin:   admin         / admin123")
    print(f"  (Or use the 1-click Quick Demo Sign-in buttons!)")
    print(f"=======================================================\n")
    
    app.run(host='127.0.0.1', port=port, debug=True)
