# Software Design Specification (SDS)
## Document 5: User Interface Design

**Version:** 1.0.0  
**Date:** 2024  
**Project:** Visitor Management System

---

## 5.1 UI Overview

The Visitor Management System provides a web-based user interface built with React. The interface is responsive and provides role-based access to different features. The UI consists of multiple pages accessible through a navigation menu, with authentication required for all pages except the login page.

---

## 5.2 Login Page

**File:** `frontend/src/pages/Login.jsx`

**Purpose:** User authentication and system entry point.

**UI Elements:**
- Username input field
- Password input field
- Login button
- Error message display area

**Behavior:**
- User enters username and password
- On submit, sends POST request to `/auth/login`
- On success, stores JWT token in localStorage
- Redirects to dashboard
- On error, displays error message

[Screenshot Placeholder: Login Page]

---

## 5.3 Dashboard

**File:** `frontend/src/pages/Dashboard.jsx`

**Purpose:** System overview and statistics display.

**UI Elements:**
- Statistics cards:
  - Active Visitors count
  - Total Visits count
  - Pending Approvals count
  - Active Employees count
- Active Visits table
- Alerts section

**Behavior:**
- Loads statistics on component mount
- Displays real-time data from backend
- Updates automatically via context refresh
- Clickable cards for navigation (if implemented)

[Screenshot Placeholder: Dashboard Page]

---

## 5.4 Visitor Management

**File:** `frontend/src/pages/VisitorEntry.jsx`

**Purpose:** Visitor registration and visit creation.

**UI Elements:**
- Visitor Registration Form:
  - Full Name input
  - CNIC input (with format validation)
  - Contact Number input (optional)
  - Register Visitor button
- Visit Creation Form:
  - Visitor selection (search by CNIC or ID)
  - Site selection dropdown
  - Host Employee selection dropdown (optional)
  - Purpose Details textarea
  - Create Visit button
- QR Code Generation:
  - Email input field
  - Generate QR Code button
  - QR code display (after generation)
  - Download QR button

**Behavior:**
- Validates CNIC format (XXXXX-XXXXXXX-X)
- On visitor registration, creates visitor record
- On visit creation, creates visit record
- On QR generation, generates QR code and sends email
- Displays success/error toast notifications
- Refreshes data context after successful operations

[Screenshot Placeholder: Visitor Entry Page]

---

## 5.5 QR Scanning

**File:** `frontend/src/pages/CheckInOut.jsx`

**Purpose:** QR code scanning for visitor check-in/check-out and employee attendance.

**UI Elements:**
- Camera view (for QR scanning)
- Manual QR code entry input
- Scan button
- Check-In button (for visitors)
- Check-Out button (for visitors)
- Status display area
- Camera selection dropdown (if multiple cameras)

**Behavior:**
- Requests camera permission on page load
- Displays live camera feed
- Scans QR codes automatically
- Verifies QR code type (employee/visitor)
- For visitors: shows check-in/check-out buttons
- For employees: processes attendance automatically
- Displays scan results and status
- Shows error messages for invalid/expired QR codes

[Screenshot Placeholder: Check-In/Out Page with Camera]

---

## 5.6 Employee Management

**File:** `frontend/src/pages/EmployeeManagement.jsx`

**Purpose:** Employee creation and management.

**UI Elements:**
- "Add New Employee" button (toggles form)
- Create Employee Form:
  - Name input
  - Hourly Rate input (number, min 0)
  - Department selection dropdown
  - Create Employee button
- Employee List Table:
  - Employee ID
  - Name
  - Department
  - Hourly Rate

**Behavior:**
- Loads departments on component mount
- Validates form inputs before submission
- On success, refreshes employee list via context
- Shows success/error toast notifications
- Form hides after successful creation

[Screenshot Placeholder: Employee Management Page]

---

## 5.7 Salary Calculation

**File:** `frontend/src/pages/SalaryCalculation.jsx`

**Purpose:** Employee salary calculation and reporting.

**UI Elements:**
- Employee selection dropdown
- Start Date picker
- End Date picker
- Calculate Salary button
- Salary Report Section (displayed after calculation):
  - Summary cards:
    - Employee Name
    - Department
    - Hourly Rate
    - Period
    - Total Days Worked
    - Total Hours
    - Total Salary (highlighted)
  - Daily Breakdown table:
    - Date
    - Sign-In Time
    - Sign-Out Time
    - Hours Worked
    - Notes (for incomplete days)
  - Export to Excel button

**Behavior:**
- Sets default date range (last 30 days) on mount
- Validates date range (start < end)
- On calculate, fetches salary data from backend
- Displays summary and daily breakdown
- On export, downloads Excel file
- Shows loading state during calculation

[Screenshot Placeholder: Salary Calculation Page]

---

## 5.8 Employee Attendance

**File:** `frontend/src/pages/EmployeeAttendance.jsx`

**Purpose:** View employee attendance logs and status.

**UI Elements:**
- Employee selection dropdown
- Employee Status display:
  - Current Status (signed in/out)
  - Last Scan Time
- Attendance Logs table:
  - Date/Time
  - Status (signin/signout)
  - Notes

**Behavior:**
- Loads employees on component mount
- On employee selection, fetches status and logs
- Displays attendance history
- Updates in real-time (if polling implemented)

[Screenshot Placeholder: Employee Attendance Page]

---

## 5.9 Employee QR Generation

**File:** `frontend/src/pages/EmployeeQR.jsx`

**Purpose:** Generate permanent QR codes for employees.

**UI Elements:**
- Employee ID input field
- Generate QR Code button
- QR Code display area (after generation)
- Download QR Code button
- Employee information display

**Behavior:**
- Validates employee ID
- On generation, creates QR code and displays it
- Allows download of QR code image
- Shows employee information

[Screenshot Placeholder: Employee QR Page]

---

## 5.10 System Logs

**File:** `frontend/src/pages/VisitLogs.jsx`

**Purpose:** View and export access logs.

**UI Elements:**
- Date Range Filters:
  - Start Date picker
  - End Date picker
  - Action Type filter dropdown
  - Apply Filters button
- Access Logs Table:
  - Log ID
  - User
  - Action
  - Details
  - Timestamp
- Export to Excel button
- Log count display

**Behavior:**
- Loads logs on component mount
- Applies filters on button click
- Displays up to 1000 most recent logs
- On export, downloads Excel file with filtered data
- Shows loading state during fetch

[Screenshot Placeholder: Visit Logs Page]

---

## 5.11 User Management

**File:** `frontend/src/pages/UserManagement.jsx`

**Purpose:** Manage system users (admin-only).

**UI Elements:**
- Create User Form:
  - Username input
  - Password input
  - Role selection (admin/security)
  - Create User button
- User List Table:
  - User ID
  - Username
  - Role
  - Created At
  - Actions (Deactivate button)

**Behavior:**
- Admin-only access (redirects if not admin)
- Validates username uniqueness
- On creation, refreshes user list
- On deactivation, shows confirmation and updates list
- Shows success/error toast notifications

[Screenshot Placeholder: User Management Page]

---

## 5.12 Site Management

**File:** `frontend/src/pages/SiteManagement.jsx`

**Purpose:** Manage sites (admin-only).

**UI Elements:**
- Create Site Form:
  - Site Name input
  - Address textarea (optional)
  - Create Site button
- Site List Table:
  - Site ID
  - Site Name
  - Address

**Behavior:**
- Admin-only access
- Validates site name uniqueness
- On creation, refreshes site list
- Shows success/error toast notifications

[Screenshot Placeholder: Site Management Page]

---

## 5.13 Admin Profile

**File:** `frontend/src/pages/AdminProfile.jsx`

**Purpose:** Display admin user profile information.

**UI Elements:**
- User Information Display:
  - Username
  - Role
  - Created At
- Logout button

**Behavior:**
- Fetches current user info on mount
- Displays user information
- Logout clears token and redirects to login

[Screenshot Placeholder: Admin Profile Page]

---

## 5.14 Layout and Navigation

**File:** `frontend/src/components/Layout.jsx`

**Purpose:** Main application layout with navigation.

**UI Elements:**
- Header:
  - Application title/logo
  - User information display
  - Logout button
- Sidebar Navigation Menu:
  - Dashboard
  - Visitor Entry
  - Check-In/Out
  - Employee QR
  - Employee Attendance
  - Employee Management (admin only)
  - Salary Calculation (admin only)
  - System Logs
  - User Management (admin only)
  - Site Management (admin only)
  - Profile
- Main Content Area:
  - Route outlet (displays current page)

**Behavior:**
- Shows/hides menu items based on user role
- Highlights active menu item
- Handles navigation between pages
- Displays user role and username
- Logout clears token and redirects

[Screenshot Placeholder: Layout with Navigation]

---

## 5.15 Common UI Components

### Toast Notifications

**Library:** react-toastify

**Usage:**
- Success notifications (green)
- Error notifications (red)
- Info notifications (blue)
- Warning notifications (orange)

**Behavior:**
- Auto-dismiss after 3 seconds
- Manual dismiss option
- Stack multiple notifications

### Loading Spinner

**Usage:**
- Displayed during API calls
- Centered on page or component
- Replaces content during loading

### Form Validation

**Behavior:**
- Real-time validation feedback
- Required field indicators (*)
- Error messages below inputs
- Disabled submit button until valid

### Tables

**Features:**
- Sortable columns (if implemented)
- Responsive design
- Alternating row colors
- Hover effects

---

## 5.16 Responsive Design

**Breakpoints:**
- Desktop: > 1024px (full layout)
- Tablet: 768px - 1024px (collapsible sidebar)
- Mobile: < 768px (stacked layout, hamburger menu)

**Behavior:**
- Navigation menu collapses on mobile
- Tables scroll horizontally on small screens
- Forms stack vertically on mobile
- Touch-friendly button sizes

---

## 5.17 Error Handling

**UI Behavior:**
- Network errors: Toast notification with retry option
- Validation errors: Inline error messages
- Authentication errors: Redirect to login
- 404 errors: Error page (if implemented)
- 500 errors: Generic error message

---

**End of Document 5: User Interface Design**

