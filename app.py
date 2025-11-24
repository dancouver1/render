from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"), echo=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def list_users():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM "USER" ORDER BY user_id'))
        users = result.fetchall()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    INSERT INTO "USER" (email, given_name, surname, city, phone_number, profile_description, password)
                    VALUES (:email, :given_name, :surname, :city, :phone_number, :profile_description, :password)
                """)
                conn.execute(query, {
                    'email': request.form['email'],
                    'given_name': request.form['given_name'],
                    'surname': request.form['surname'],
                    'city': request.form['city'],
                    'phone_number': request.form['phone_number'],
                    'profile_description': request.form['profile_description'],
                    'password': request.form['password']
                })
                conn.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('user_form.html', user=None)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    UPDATE "USER"
                    SET email = :email, given_name = :given_name, surname = :surname,
                        city = :city, phone_number = :phone_number,
                        profile_description = :profile_description, password = :password
                    WHERE user_id = :user_id
                """)
                conn.execute(query, {
                    'user_id': user_id,
                    'email': request.form['email'],
                    'given_name': request.form['given_name'],
                    'surname': request.form['surname'],
                    'city': request.form['city'],
                    'phone_number': request.form['phone_number'],
                    'profile_description': request.form['profile_description'],
                    'password': request.form['password']
                })
                conn.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM "USER" WHERE user_id = :user_id'), {'user_id': user_id})
        user = result.fetchone()
    return render_template('user_form.html', user=user)

@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM "USER" WHERE user_id = :user_id'), {'user_id': user_id})
            conn.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('list_users'))

@app.route('/caregivers')
def list_caregivers():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.*, u.given_name, u.surname, u.email, u.phone_number
            FROM CAREGIVER c
            JOIN "USER" u ON c.caregiver_user_id = u.user_id
            ORDER BY c.caregiver_user_id
        """))
        caregivers = result.fetchall()
    return render_template('caregivers.html', caregivers=caregivers)

@app.route('/caregivers/add', methods=['GET', 'POST'])
def add_caregiver():
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    INSERT INTO CAREGIVER (caregiver_user_id, photo, gender, caregiving_type, hourly_rate)
                    VALUES (:caregiver_user_id, :photo, :gender, :caregiving_type, :hourly_rate)
                """)
                conn.execute(query, {
                    'caregiver_user_id': request.form['caregiver_user_id'],
                    'photo': request.form['photo'],
                    'gender': request.form['gender'],
                    'caregiving_type': request.form['caregiving_type'],
                    'hourly_rate': request.form['hourly_rate']
                })
                conn.commit()
            flash('Caregiver added successfully!', 'success')
            return redirect(url_for('list_caregivers'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT user_id, given_name, surname FROM "USER"
            WHERE user_id NOT IN (SELECT caregiver_user_id FROM CAREGIVER)
            ORDER BY given_name
        """))
        available_users = result.fetchall()
    return render_template('caregiver_form.html', caregiver=None, users=available_users)

@app.route('/caregivers/edit/<int:caregiver_user_id>', methods=['GET', 'POST'])
def edit_caregiver(caregiver_user_id):
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    UPDATE CAREGIVER
                    SET photo = :photo, gender = :gender,
                        caregiving_type = :caregiving_type, hourly_rate = :hourly_rate
                    WHERE caregiver_user_id = :caregiver_user_id
                """)
                conn.execute(query, {
                    'caregiver_user_id': caregiver_user_id,
                    'photo': request.form['photo'],
                    'gender': request.form['gender'],
                    'caregiving_type': request.form['caregiving_type'],
                    'hourly_rate': request.form['hourly_rate']
                })
                conn.commit()
            flash('Caregiver updated successfully!', 'success')
            return redirect(url_for('list_caregivers'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM CAREGIVER WHERE caregiver_user_id = :caregiver_user_id'),
                            {'caregiver_user_id': caregiver_user_id})
        caregiver = result.fetchone()
    return render_template('caregiver_form.html', caregiver=caregiver, users=None)

@app.route('/caregivers/delete/<int:caregiver_user_id>')
def delete_caregiver(caregiver_user_id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM CAREGIVER WHERE caregiver_user_id = :caregiver_user_id'),
                       {'caregiver_user_id': caregiver_user_id})
            conn.commit()
        flash('Caregiver deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('list_caregivers'))

@app.route('/appointments')
def list_appointments():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT a.*, 
                   uc.given_name || ' ' || uc.surname AS caregiver_name,
                   um.given_name || ' ' || um.surname AS member_name
            FROM APPOINTMENT a
            JOIN CAREGIVER c ON a.caregiver_user_id = c.caregiver_user_id
            JOIN "USER" uc ON c.caregiver_user_id = uc.user_id
            JOIN MEMBER m ON a.member_user_id = m.member_user_id
            JOIN "USER" um ON m.member_user_id = um.user_id
            ORDER BY a.appointment_date DESC
        """))
        appointments = result.fetchall()
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    INSERT INTO APPOINTMENT (caregiver_user_id, member_user_id, appointment_date,
                                           appointment_time, work_hours, status)
                    VALUES (:caregiver_user_id, :member_user_id, :appointment_date,
                           :appointment_time, :work_hours, :status)
                """)
                conn.execute(query, {
                    'caregiver_user_id': request.form['caregiver_user_id'],
                    'member_user_id': request.form['member_user_id'],
                    'appointment_date': request.form['appointment_date'],
                    'appointment_time': request.form['appointment_time'],
                    'work_hours': request.form['work_hours'],
                    'status': request.form['status']
                })
                conn.commit()
            flash('Appointment added successfully!', 'success')
            return redirect(url_for('list_appointments'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        caregivers = conn.execute(text("""
            SELECT c.caregiver_user_id, u.given_name, u.surname
            FROM CAREGIVER c JOIN "USER" u ON c.caregiver_user_id = u.user_id
            ORDER BY u.given_name
        """)).fetchall()
        
        members = conn.execute(text("""
            SELECT m.member_user_id, u.given_name, u.surname
            FROM MEMBER m JOIN "USER" u ON m.member_user_id = u.user_id
            ORDER BY u.given_name
        """)).fetchall()
    
    return render_template('appointment_form.html', appointment=None, caregivers=caregivers, members=members)

@app.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    UPDATE APPOINTMENT
                    SET appointment_date = :appointment_date, appointment_time = :appointment_time,
                        work_hours = :work_hours, status = :status
                    WHERE appointment_id = :appointment_id
                """)
                conn.execute(query, {
                    'appointment_id': appointment_id,
                    'appointment_date': request.form['appointment_date'],
                    'appointment_time': request.form['appointment_time'],
                    'work_hours': request.form['work_hours'],
                    'status': request.form['status']
                })
                conn.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('list_appointments'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM APPOINTMENT WHERE appointment_id = :appointment_id'),
                            {'appointment_id': appointment_id})
        appointment = result.fetchone()
    
    return render_template('appointment_form.html', appointment=appointment, caregivers=None, members=None)

@app.route('/appointments/delete/<int:appointment_id>')
def delete_appointment(appointment_id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM APPOINTMENT WHERE appointment_id = :appointment_id'),
                       {'appointment_id': appointment_id})
            conn.commit()
        flash('Appointment deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('list_appointments'))

@app.route('/jobs')
def list_jobs():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT j.*, u.given_name || ' ' || u.surname AS member_name
            FROM JOB j
            JOIN MEMBER m ON j.member_user_id = m.member_user_id
            JOIN "USER" u ON m.member_user_id = u.user_id
            ORDER BY j.date_posted DESC
        """))
        jobs = result.fetchall()
    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        try:
            with engine.connect() as conn:
                query = text("""
                    INSERT INTO JOB (member_user_id, required_caregiving_type, other_requirements, date_posted)
                    VALUES (:member_user_id, :required_caregiving_type, :other_requirements, :date_posted)
                """)
                conn.execute(query, {
                    'member_user_id': request.form['member_user_id'],
                    'required_caregiving_type': request.form['required_caregiving_type'],
                    'other_requirements': request.form['other_requirements'],
                    'date_posted': request.form['date_posted']
                })
                conn.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('list_jobs'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    with engine.connect() as conn:
        members = conn.execute(text("""
            SELECT m.member_user_id, u.given_name, u.surname
            FROM MEMBER m JOIN "USER" u ON m.member_user_id = u.user_id
            ORDER BY u.given_name
        """)).fetchall()
    
    return render_template('job_form.html', job=None, members=members)

@app.route('/jobs/delete/<int:job_id>')
def delete_job(job_id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM JOB WHERE job_id = :job_id'), {'job_id': job_id})
            conn.commit()
        flash('Job deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('list_jobs'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


