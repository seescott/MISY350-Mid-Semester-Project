"""
Unified Code Manager refactoring practice.

This starter is intentionally designed as a one-class Streamlit app. It works,
but the class has too many reasons to change. Use it for a classroom review of
data, service, and UI responsibilities before breaking it into smaller classes.

Before refactoring, run the app once and try the core flow: generate a code,
use it, deactivate it, and restart the app. Use that same flow after each phase
to check that behavior stayed the same.

Run with:
    streamlit run files/practice_unified_code_manager_starter.py
"""

import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import streamlit as st


# Keep the data file beside this starter so students can inspect persistence.
DATA_FILE = Path(__file__).with_name("unified_codes.json")
CODE_TYPES = ["attendance", "help", "quiz", "assignment", "enrollment"]


class UnifiedCodeManager:
    """One large class that manages access codes and draws the UI."""

    def __init__(self, json_path: Path) -> None:
        self.json_path = json_path
        self.codes = self.load_codes()

    def load_codes(self) -> list[dict[str, Any]]:
        if not self.json_path.exists():
            return []

        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            st.error("The codes JSON file is not valid.")
            return []

        if not isinstance(data, list):
            st.error("The codes JSON file should contain a list.")
            return []

        return data

    def save_codes(self) -> None:
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(self.codes, file, indent=2)

    def generate_code(
        self,
        code_type: str,
        course_id: str,
        created_by: str,
        expiry_minutes: Optional[int] = None,
        max_uses: Optional[int] = None,
        description: str = "",
    ) -> str:
        code = self._generate_unique_code()
        expires_at = None

        if expiry_minutes:
            expires_at = datetime.now() + timedelta(minutes=expiry_minutes)

        new_code = {
            "code": code,
            "code_type": code_type,
            "course_id": course_id,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "expires_at": expires_at.isoformat(timespec="seconds") if expires_at else None,
            "max_uses": max_uses,
            "current_uses": 0,
            "is_active": True,
            "description": description,
            "usage_log": [],
        }

        self.codes.append(new_code)
        self.save_codes()
        return code

    def get_codes(
        self,
        course_id: str,
        code_type: Optional[str] = None,
        active_only: bool = True,
    ) -> list[dict[str, Any]]:
        results = []

        for item in self.codes:
            if item["course_id"] != course_id:
                continue
            if code_type and item["code_type"] != code_type:
                continue
            if active_only and not item["is_active"]:
                continue
            results.append(item)

        return sorted(results, key=lambda item: item["created_at"], reverse=True)

    def use_code(self, code: str, user_id: str) -> dict[str, Any]:
        code_data = self._find_code(code)

        if code_data is None:
            return {"success": False, "message": "Invalid code."}

        if not code_data["is_active"]:
            return {"success": False, "message": "Code is inactive."}

        if code_data["expires_at"]:
            expires_at = datetime.fromisoformat(code_data["expires_at"])
            if datetime.now() > expires_at:
                return {"success": False, "message": "Code has expired."}

        if code_data["max_uses"] and code_data["current_uses"] >= code_data["max_uses"]:
            return {"success": False, "message": "Code usage limit reached."}

        code_data["current_uses"] += 1
        code_data["usage_log"].append(
            {
                "user_id": user_id,
                "used_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        self.save_codes()

        return {
            "success": True,
            "message": "Code used successfully.",
            "code_type": code_data["code_type"],
            "course_id": code_data["course_id"],
        }

    def deactivate_code(self, code: str) -> bool:
        code_data = self._find_code(code)

        if code_data is None:
            return False

        code_data["is_active"] = False
        self.save_codes()
        return True

    def deactivate_expired_codes(self, course_id: str) -> int:
        count = 0
        now = datetime.now()

        for item in self.codes:
            if item["course_id"] != course_id:
                continue
            if not item["expires_at"]:
                continue
            if datetime.fromisoformat(item["expires_at"]) < now and item["is_active"]:
                item["is_active"] = False
                count += 1

        if count > 0:
            self.save_codes()

        return count

    def deactivate_all_help_codes(self, course_id: str) -> int:
        count = 0

        for item in self.codes:
            if item["course_id"] == course_id and item["code_type"] == "help" and item["is_active"]:
                item["is_active"] = False
                count += 1

        if count > 0:
            self.save_codes()

        return count

    def get_summary(self, course_id: str) -> dict[str, Any]:
        course_codes = self.get_codes(course_id, active_only=False)
        total = len(course_codes)
        active = len([item for item in course_codes if item["is_active"]])
        total_uses = sum(item["current_uses"] for item in course_codes)

        type_counts = {}
        for item in course_codes:
            code_type = item["code_type"]
            type_counts[code_type] = type_counts.get(code_type, 0) + 1

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "total_uses": total_uses,
            "type_counts": type_counts,
        }

    def show(self) -> None:
        st.title("Unified Code Manager")

        if "course_id" not in st.session_state:
            st.session_state["course_id"] = "MISY350"
        if "teacher_id" not in st.session_state:
            st.session_state["teacher_id"] = "instructor_1"

        course_id = st.session_state["course_id"]
        teacher_id = st.session_state["teacher_id"]

        tab_generate, tab_manage, tab_student = st.tabs(
            ["Generate Codes", "Manage Codes", "Try a Code"]
        )

        with tab_generate:
            self.show_generate_tab(course_id, teacher_id)

        with tab_manage:
            self.show_manage_tab(course_id)

        with tab_student:
            self.show_try_code_tab()

    def show_generate_tab(self, course_id: str, teacher_id: str) -> None:
        st.subheader("Generate New Access Code")

        with st.form("generate_code_form"):
            code_type = st.selectbox("Code type", CODE_TYPES)
            description = st.text_input("Description")
            set_expiration = st.checkbox("Set expiration", value=True)
            expiry_minutes = None

            if set_expiration:
                expiry_minutes = st.slider(
                    "Expires in minutes",
                    min_value=5,
                    max_value=240,
                    value=30,
                    step=5,
                )

            set_max_uses = st.checkbox("Set usage limit")
            max_uses = None

            if set_max_uses:
                max_uses = st.number_input(
                    "Maximum uses",
                    min_value=1,
                    max_value=200,
                    value=30,
                    step=1,
                )

            submitted = st.form_submit_button("Generate code", type="primary")

        if submitted:
            code = self.generate_code(
                code_type=code_type,
                course_id=course_id,
                created_by=teacher_id,
                expiry_minutes=expiry_minutes,
                max_uses=int(max_uses) if max_uses else None,
                description=description,
            )
            st.success(f"Generated code: {code}")
            st.rerun()

        st.subheader("Recent Codes")
        recent_codes = self.get_codes(course_id, active_only=True)
        if recent_codes:
            st.dataframe(
                self._format_codes_for_display(recent_codes[:5]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No active codes yet.")

    def show_manage_tab(self, course_id: str) -> None:
        st.subheader("Code Management")

        summary = self.get_summary(course_id)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", summary["total"])
        col2.metric("Active", summary["active"])
        col3.metric("Inactive", summary["inactive"])
        col4.metric("Uses", summary["total_uses"])

        st.write("Code type counts")
        st.json(summary["type_counts"])

        filter_type = st.selectbox("Filter by type", ["all"] + CODE_TYPES)
        filter_status = st.selectbox("Filter by status", ["active", "inactive", "all"])
        search = st.text_input("Search by code or description")

        active_only = filter_status == "active"
        codes = self.get_codes(
            course_id=course_id,
            code_type=None if filter_type == "all" else filter_type,
            active_only=active_only,
        )

        if filter_status == "inactive":
            codes = [item for item in codes if not item["is_active"]]

        if search:
            search_text = search.lower()
            codes = [
                item
                for item in codes
                if search_text in item["code"].lower()
                or search_text in item["description"].lower()
            ]

        if codes:
            st.dataframe(
                self._format_codes_for_display(codes),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No codes match the current filters.")

        st.divider()
        st.subheader("Actions")

        active_codes = [item["code"] for item in self.get_codes(course_id, active_only=True)]
        selected_code = st.selectbox("Select an active code", [""] + active_codes)

        if st.button("Deactivate selected code") and selected_code:
            if self.deactivate_code(selected_code):
                st.success(f"{selected_code} was deactivated.")
                st.rerun()
            else:
                st.error("Code was not found.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Deactivate expired codes"):
                count = self.deactivate_expired_codes(course_id)
                st.success(f"Deactivated {count} expired code(s).")
                st.rerun()

        with col2:
            if st.button("Deactivate all help codes"):
                count = self.deactivate_all_help_codes(course_id)
                st.success(f"Deactivated {count} help code(s).")
                st.rerun()

    def show_try_code_tab(self) -> None:
        st.subheader("Try a Code")

        user_id = st.text_input("Student id", value="student_1")
        code = st.text_input("Code").strip().upper()

        if st.button("Use code"):
            result = self.use_code(code, user_id)

            if result["success"]:
                st.success(result["message"])
                st.json(result)
            else:
                st.error(result["message"])

    def _format_codes_for_display(self, codes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = []

        for item in codes:
            rows.append(
                {
                    "Code": item["code"],
                    "Type": item["code_type"],
                    "Description": item["description"],
                    "Created": item["created_at"],
                    "Expires": item["expires_at"] or "Never",
                    "Uses": f"{item['current_uses']}/{item['max_uses'] or 'unlimited'}",
                    "Active": item["is_active"],
                }
            )

        return rows

    def _generate_unique_code(self) -> str:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        if self._find_code(code):
            return self._generate_unique_code()

        return code

    def _find_code(self, code: str) -> Optional[dict[str, Any]]:
        for item in self.codes:
            if item["code"] == code:
                return item
        return None


def main() -> None:
    manager = UnifiedCodeManager(DATA_FILE)
    manager.show()


if __name__ == "__main__":
    main()
