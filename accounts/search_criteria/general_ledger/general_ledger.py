# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.

#get company letter head
#---------------------------------------------------------------------
from __future__ import unicode_literals
l_head = sql("select content from `tabLetter Head` where ifnull(is_default, 0) = 1 and ifnull(disabled, 0) = 0")
l_head = l_head and l_head[0][0] or ''


# Posting date, fiscal year and year start date
#---------------------------------------------------------------------
if not filter_values.get('posting_date') or not filter_values.get('posting_date1'):
	msgprint("Please enter From Date and To Date")
	raise Exception
else:
	from_date = filter_values['posting_date']
	to_date = filter_values['posting_date1']

from_date_year = sql("select name from `tabFiscal Year` where %s between year_start_date and date_sub(date_add(year_start_date,interval 1 year), interval 1 day)",from_date)
if not from_date_year:
	msgprint("From Date is out of range. Please check.", raise_exception=1)
else:
	from_date_year = from_date_year[0][0]
#to_date_year = sql("select name from `tabFiscal Year` where %s between year_start_date and date_sub(date_add(year_start_date,interval 1 year), interval 1 day)",to_date)[0][0]


# define columns
#---------------------------------------------------------------------
col = []
col.append(['Date','Date','80px',''])
col.append(['Detail','Text','475px',''])
col.append(['Debit','Currency','75px',''])
col.append(['Credit','Currency','75px',''])

for c in col:
	colnames.append(c[0])
	coltypes.append(c[1])
	colwidths.append(c[2])
	coloptions.append(c[3])
	col_idx[c[0]] = len(colnames)


#total query
#---------------------------------------------------------------------
total_debit, total_credit, total_opening, total_diff = 0,0,0,0
q = query.split('WHERE')[1].split('LIMIT')
if len(q) > 2:
	query_where_clause = 'LIMIT'.join(q[:-1])
else:
	query_where_clause = q[0]

tot = sql('select sum(debit),sum(credit) from `tabGL Entry` where %s' % query_where_clause)

for t in tot:
	total_debit += t and flt(t[0]) or 0
	total_credit += t and flt(t[1]) or 0

total_diff = total_debit - total_credit

out = []


# If account mentioned, show opening and closing
#---------------------------------------------------------------------
account = filter_values.get('account')

if account and (total_debit != 0 or total_credit != 0):
	acc_det = sql("select debit_or_credit, is_pl_account, lft, rgt, group_or_ledger from tabAccount where name = '%s'" % account)

	from accounts.utils import get_balance_on
	opening_bal = get_balance_on(account, add_days(from_date, -1))
	closing_bal = get_balance_on(account, to_date)
	
	if acc_det[0][0] == 'Credit':
		closing_bal = -1*closing_bal
		opening_bal = -1*opening_bal

	# add opening row
	t_row = ['' for i in range(len(colnames))]
	t_row[1] = 'Opening as on '+formatdate(from_date)
	t_row[col_idx['Debit']-1] = opening_bal
	out.append(t_row)
	
	
# table output
#---------------------------------------------------------------------
count = 0
for r in res:
	count +=1
	det = r[1].split('~~~')
	if from_export == 1:
		a = "Account: " + det[0] + NEWLINE + det[1] + NEWLINE + "Against: " + det[2] + NEWLINE + "Voucher No: " + det[4]
	else:
		a = "Account: <b>" + det[0]+ "</b>" + NEWLINE + "<div class='comment'>" +det[1]+ "</div><div class = 'comment' style='padding-left:12px'>Against: <b>" + det[2] + "</b></div><div class = 'comment' style='padding-left:12px'>Voucher No: <span class='link_type' onclick='loaddoc(" + '"' + det[3] +'", ' + '"' + det[4] +'"' + ")'>" + det[4] + "</span></div>"
	r[1] = a
	out.append(r)


# Total, Difference and closing balance
#---------------------------------------------------------------------
if total_debit != 0 or total_credit != 0:
	# Total debit/credit
	t_row = ['' for i in range(len(colnames))]
	t_row[1] = 'Total'
	t_row[col_idx['Debit']-1] = total_debit
	t_row[col_idx['Credit']-1] = total_credit
	out.append(t_row)

	# diffrence (dr-cr)
	t_row = ['' for i in range(len(colnames))]
	t_row[1] = 'Total(Dr-Cr)'
	t_row[col_idx['Debit']-1] = total_diff
	out.append(t_row)

	# closing
	if account:
		t_row = ['' for i in range(len(colnames))]
		t_row[1] = 'Closing Balance on ' + formatdate(to_date)
		t_row[col_idx['Debit']-1] = flt(closing_bal)
		out.append(t_row)


# Print Format
#---------------------------------------------------------------------
myheader = """<table width = '100%%'><tr><td>"""+l_head+"""</td>
</tr>
<tr> <td>
<div><h3> %(acc)s </h3></div>
<div>Ledger Between %(fdt)s and %(tdt)s </div></td></tr></table><br>

	""" % {'acc':account,
				 'fdt':from_date,
				 'tdt':to_date}

page_template = myheader+"<div>%(table)s</div>"
