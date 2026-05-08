import streamlit as st
import requests
import datetime as dt

# =========================
# CONFIG
# =========================
base_url = "http://127.0.0.1:8000"

st.set_page_config(page_title="Appointment System", layout="centered")

st.title("Appointment Booking System")

# =========================================================
# SCHEDULE APPOINTMENT
# =========================================================

st.subheader("Schedule Appointment")

patient_name = st.text_input( "Patient Name",key="patient_name")

reason = st.text_area("Reason",key="reason")

start_date = st.date_input( "Appointment Date", key="start_date",value=dt.date.today())

start_time = st.time_input( "Appointment Time",key="start_time",value=dt.time(9, 0))

if st.button("Schedule Appointment"):

    start_dt = dt.datetime.combine(start_date, start_time)

    payload = {
        "patient_name": patient_name.strip(),
        "reason": reason.strip() or None,
        "start_time": start_dt.isoformat()
    }

    try:
        resp = requests.post(
            f"{base_url}/schedule_appointments/",
            json=payload,
            timeout=10
        )

        resp.raise_for_status()

        data = resp.json()

        st.success("Appointment Scheduled Successfully")

        st.json(data)

    except requests.HTTPError:
        st.error(resp.text)

    except requests.ConnectionError:
        st.error("Backend server is not running")

    except requests.Timeout:
        st.error("Request timed out")

    except requests.RequestException as exc:
        st.error(f"Schedule failed: {exc}")

# =========================================================
# CANCEL APPOINTMENT
# =========================================================

st.divider()


st.subheader("Cancel Appointment")

cancel_date = st.date_input("Date to view appointments", key="cancel_date", value=dt.date.today())

if st.button("Load Appointments for Cancellation"):
    resp = requests.get(f"{base_url}/list_appointments/", params={"date": cancel_date.isoformat()}, timeout=10)
    if resp.ok:
        st.session_state["cancel_list"] = resp.json()

if "cancel_list" in st.session_state and st.session_state["cancel_list"]:
    appts = st.session_state["cancel_list"]

    options = {
        f"ID {a['id']} — {a['patient_name']} at {a['start_time'][11:16]}": a
        for a in appts
    }

    selected_label = st.selectbox("Select appointment to cancel", list(options.keys()))
    selected = options[selected_label]

    if st.button("Cancel Selected Appointment"):
        payload = {
            "patient_name": selected["patient_name"],
            "date": cancel_date.isoformat(),
            "appointment_id": selected["id"]   # sends ID so backend cancels exact record
        }

        try:
            resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.success(f"Cancelled {data['canceled_cnt']} appointment(s) for {data['patient_name']}")
            del st.session_state["cancel_list"]
            st.rerun()
        except requests.HTTPError:
            st.error(resp.text)
        except requests.ConnectionError:
            st.error("Backend server is not running")

# =========================================================
# LIST APPOINTMENTS
# =========================================================

st.divider()

st.subheader("Check Appointments")

appointments_date = st.date_input( "Date to check appointments",key="check_appointment_date",value=dt.date.today())

if st.button("Check Appointments"):

    try:

        params = {
            "date": appointments_date.isoformat()
        }

        resp = requests.get(
            f"{base_url}/list_appointments/",
            params=params,
            timeout=10
        )

        resp.raise_for_status()

        data = resp.json()

        if data:
            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No appointments found")

    except requests.HTTPError:
        st.error(resp.text)

    except requests.ConnectionError:
        st.error("Backend server is not running")

    except requests.Timeout:
        st.error("Request timed out")

    except requests.RequestException as exc:
        st.warning(f"Could not load appointments: {exc}")