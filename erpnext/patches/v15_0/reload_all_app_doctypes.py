# erpnext/patches/v15_0/reload_all_app_doctypes.py
import frappe
import os

APP_NAME = 'erpnext'

def execute():
    """Reload all DocTypes defined within the ERPNext app."""
    frappe.flags.ignore_permissions = True
    frappe.db.auto_commit_on_many_writes = True

    app_path = frappe.get_app_path(APP_NAME)
    if not os.path.exists(app_path):
        frappe.log_error(f"App path not found for {APP_NAME}", "Patch: Reload All ERPNext DocTypes")
        frappe.flags.ignore_permissions = False
        frappe.db.auto_commit_on_many_writes = False
        return

    print(f"Starting reload for DocTypes in app: {APP_NAME}. This may take a long time...")
    reloaded_count = 0
    error_count = 0
    skipped_single = 0

    for module_name in os.listdir(app_path):
        module_path = os.path.join(app_path, module_name)
        if not os.path.isdir(module_path):
            continue

        doctype_path = os.path.join(module_path, "doctype")
        if not os.path.isdir(doctype_path):
            continue

        for doctype_name in os.listdir(doctype_path):
            doctype_folder = os.path.join(doctype_path, doctype_name)
            doctype_json = os.path.join(doctype_folder, doctype_name + ".json")
            doctype_py = os.path.join(doctype_folder, doctype_name + ".py")

            is_single = False
            if os.path.isfile(doctype_py):
                try:
                    with open(doctype_py, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'frappe.model.document.Document' not in content and \
                           'frappe.model.document import Document' not in content:
                                 is_single = True
                except Exception:
                    pass

            if os.path.isdir(doctype_folder) and os.path.isfile(doctype_json):
                if is_single:
                     skipped_single += 1
                     continue

                try:
                    print(f"  Reloading DocType: {module_name} / {doctype_name} ... ", end="")
                    frappe.reload_doc(module_name, 'doctype', doctype_name, force=True)
                    print("Done")
                    reloaded_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"ERROR reloading {doctype_name}: {e}")
                    frappe.log_error(f"Error reloading ERPNext DocType {doctype_name}: {e}", "Patch: Reload All App DocTypes")

    frappe.db.commit()
    frappe.flags.ignore_permissions = False
    frappe.db.auto_commit_on_many_writes = False

    print("-" * 40)
    print(f"Finished reloading DocTypes for app: {APP_NAME}")
    print(f"Successfully reloaded: {reloaded_count}")
    print(f"Skipped (Single DocTypes): {skipped_single}")
    print(f"Errors encountered: {error_count}")
    print("-" * 40) 