import frappe

def execute():
	"""
	Patch to update the relationship between Asset Capitalization Stock Item and Purchase Receipt Item.
	This patch is designed to handle the situation where the table might not exist in the database.
	"""
	# First check if the table exists
	try:
		# Check if the table exists by trying to get its columns
		columns = frappe.db.get_table_columns("tabAsset Capitalization Stock Item")
		
		# If we get here, the table exists, so check for the purchase_receipt_item field
		if "purchase_receipt_item" in columns:
			frappe.db.sql(
				"""
				UPDATE `tabAsset Capitalization Stock Item` ACSI
				INNER JOIN `tabPurchase Receipt Item` PRI 
					ON ACSI.item_code = PRI.item_code 
					AND ACSI.parent = PRI.parent
				SET ACSI.purchase_receipt_item = PRI.name
				WHERE ACSI.reference_doctype = 'Purchase Receipt'
				AND ACSI.purchase_receipt_item IS NULL
				"""
			)
			print("Updated purchase_receipt_item column in Asset Capitalization Stock Item")
			frappe.db.commit()
		else:
			print("Patch skipped: purchase_receipt_item field is missing in the schema")
			
	except Exception as e:
		# Table doesn't exist or other error occurred
		print(f"Patch skipped: Asset Capitalization Stock Item table not found or other error occurred: {str(e)}")
		# No need to raise the exception, just skip the patch
		return