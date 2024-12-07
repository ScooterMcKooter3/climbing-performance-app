import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class ClimberProfile:
    def __init__(self, hardest_grade, pull_up_strength, crimp_20mm_strength, crimp_10mm_strength, pinch_grip_strength, endurance, power_endurance, hamstring_flexibility, hip_flexibility, core_strength, height, weight):
        self.hardest_grade = hardest_grade
        self.pull_up_strength = pull_up_strength
        self.crimp_20mm_strength = crimp_20mm_strength
        self.crimp_10mm_strength = crimp_10mm_strength
        self.pinch_grip_strength = pinch_grip_strength
        self.endurance = endurance
        self.power_endurance = power_endurance
        self.hamstring_flexibility = hamstring_flexibility
        self.hip_flexibility = hip_flexibility
        self.core_strength = core_strength
        self.height = height  
        self.weight = weight 
    
    def to_list(self):
        return [
            self.hardest_grade,
            self.pull_up_strength,
            self.crimp_20mm_strength,
            self.crimp_10mm_strength,
            self.pinch_grip_strength,
            self.endurance,
            self.power_endurance,
            self.hamstring_flexibility,
            self.hip_flexibility,
            self.core_strength,
            self.height,  
            self.weight
        ]

def authenticate_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"Error authenticating Google Sheets: {e}")
        raise

def save_to_google_sheets(profile, sheet_name="ClimberProfiles"):
    try:
        client = authenticate_google_sheets()
        sheet = client.open(sheet_name).sheet1
        sheet.append_row(profile.to_list())
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        raise

def load_from_google_sheets(sheet_name="ClimberProfiles"):
    try:
        client = authenticate_google_sheets()
        sheet = client.open(sheet_name).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()  # Return an empty DataFrame to avoid breaking

def analyze_user(user_profile, data):
    hardest_grade = user_profile.hardest_grade
    grade_group = data[data["Hardest Grade"] == hardest_grade]

    if grade_group.empty:
        print(f"No data found for climbers with grade {hardest_grade}.")
        return

    comparisons = {
        "Pull-Up Strength (kg)": user_profile.pull_up_strength,
        "Finger Strength on 20mm Crimp (kg)": user_profile.crimp_20mm_strength,
        "Finger Strength on 10mm Crimp (kg)": user_profile.crimp_10mm_strength,
        "Pinch Grip Strength (kg)": user_profile.pinch_grip_strength,
        "Endurance (min)": user_profile.endurance,
        "Power Endurance (Pull-Ups)": user_profile.power_endurance,
        "Hamstring Flexibility (cm)": user_profile.hamstring_flexibility,
        "Hip Flexibility (cm)": user_profile.hip_flexibility,
        "Core Strength (min)": user_profile.core_strength
    }

    print(f"\nAnalysis for climbers with grade {hardest_grade}:\n")
    for metric, user_value in comparisons.items():
        if metric in grade_group.columns and not grade_group[metric].isnull().all():
            # Calculate percentile
            percentile = (grade_group[metric] < user_value).mean() * 100
            if percentile >= 90:
                print(f"{metric}: Top {int(percentile)}th percentile. Excellent work!")
            elif percentile <= 10:
                print(f"{metric}: Bottom {int(percentile)}th percentile. Focus on improving.")
            else:
                print(f"{metric}: {int(percentile)}th percentile.")
        else:
            print(f"{metric}: Insufficient data for analysis.")

def get_float_input(prompt, allow_negative=False):
    while True:
        try:
            value = float(input(prompt))
            if not allow_negative and value < 0:
                print("Please enter a non-negative value.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def main():
    # Load existing data from Google Sheets
    data = load_from_google_sheets()

    print("\nEnter a new climbing performance profile:")
    hardest_grade = input("Current hardest Bouldering Outside V grade: ")
    pull_up_strength = get_float_input("Max 1 Rep pull-up strength Additional Weight (kg): ")
    crimp_20mm_strength = get_float_input("Dead hang 20mm crimp Additional Weight (kg): ")
    crimp_10mm_strength = get_float_input("Dead hang  10mm crimp strength Additional Weight (kg): ")
    pinch_grip_strength = get_float_input("Dead hang strength Pinch grip  Additional Weight (kg): ")
    endurance = get_float_input("Endurance (7:3 hang board repeaters, min): ")
    power_endurance = get_float_input("Power Endurance (total body-weight pull-ups): ", allow_negative=True)
    hamstring_flexibility = get_float_input("Hamstring Flexibility (distance beyond toes, cm): ")
    hip_flexibility = get_float_input("Hip Lateral Flexibility (distance from pelvis to ground, cm): ")
    core_strength = get_float_input("Core Strength (e.g., plank duration, min): ")
    height = float(input("Height (cm): "))
    weight = float(input("Weight (kg): "))

    climber = ClimberProfile(hardest_grade, pull_up_strength, crimp_20mm_strength, crimp_10mm_strength, pinch_grip_strength, endurance, power_endurance, hamstring_flexibility, hip_flexibility, core_strength, height, weight)

    # Save to Google Sheets
    try:
        save_to_google_sheets(climber)
        print("Profile saved successfully!")
    except Exception as e:
        print(f"Failed to save profile: {e}")
        return

    # Perform analysis
    data = load_from_google_sheets()  # Reload data after saving
    if not data.empty:
        analyze_user(climber, data)
    else:
        print("Unable to perform analysis due to missing data.")

if __name__ == "__main__":
    main()
