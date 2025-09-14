import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { DashboardWelcome } from '@/pages/HomePage/components/DashboardWelcome';
import LoginPage from '@pages/LoginPage';
import SignupPage from '@pages/SignupPage';
import ForgotPasswordPage from '@pages/ForgotPasswordPage';
import ResetPasswordPage from '@pages/ResetPasswordPage';
import CreateOrganizationPage from '@pages/CreateOrganizationPage';
import OrganizationPage from '@pages/OrganizationPage';
import AcceptInvitePage from '@pages/AcceptInvitePage';
import MainLayout from '@layouts/MainLayout';
import AuthLayout from '@layouts/AuthLayout';
import AdminLayout from '@layouts/AdminLayout';
import AdminSigninPage from '@pages/AdminSigninPage';
import AdminDashboardPage from '@/pages/admin/DashboardPage';
import AccountsPage from '@/pages/modules/accounts/AccountsPage';
import AccountDetails from '@/pages/modules/AccountDetails';
import AccountEdit from '@/pages/modules/AccountEdit';
import NotesPage from '@/pages/modules/notes/NotesPage';
import NoteDetailsPage from '@/pages/modules/notes/NoteDetailsPage';
import NoteEditPage from '@/pages/modules/notes/NoteEditPage';
import NoteCreatePage from '@/pages/modules/notes/NoteCreatePage';
import AccountsUserPermissions from '@/pages/modules/AccountsUserPermissions';
import OrganizationUpdatePage from '@/pages/OrganizationUpdatePage';
import ClientSurveys from '@/pages/client-surveys';
import SignInPage from '@/pages/testUI/SignInPage';
import { ResetPasswordDialog } from '@/pages/testUI/ResetPasswordDialog';
import SetNewPassword from '@/pages/testUI/SetNewPassword';
import CreateOrganization from '@/pages/testUI/CreateOrganization';
import EditOrganizationDetails from '@/pages/testUI/EditOrganizationDetails';
import OrganizationDetailsView from '@/pages/testUI/OrganizationDetailsView';
import Dashboard from '@/pages/testUI/Dashboard';
import CreateAccountModal from '@/pages/testUI/CreateAccountModal';
import AccountOverview from '@/pages/testUI/AccountOverview';
import AccountOverviewEdit from '@/pages/testUI/AccountOverviewEdit';
import AccountContact from '@/pages/testUI/AccountContact';
import PastPerformance from '@/pages/testUI/PastPerformance';
import MyAccountNotes from '@/pages/testUI/MyAccountNotes';
import MyAccountFinancial from '@/pages/testUI/MyAccountFinancial';
import MyOpportunities from '@/pages/testUI/MyOpportunities';

// import ClientSurveys from '@/pages/client-surveys';

// # pnpm
// export PNPM_HOME="/home/rishabh/.local/share/pnpm"
// case ":$PATH:" in
//   *":$PNPM_HOME:"*) ;;
//   *) export PATH="$PNPM_HOME:$PATH" ;;
// esac

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: '',
        element: <HomePage />,
        children: [
          {
            index: true,
            element: <DashboardWelcome />,
          },
          {
            path: 'module/accounts',
            element: <AccountsPage />,
          },
          {
            path: 'module/accounts/:id',
            element: <AccountDetails />,
          },
          {
            path: 'module/accounts/:id/edit',
            element: <AccountEdit />,
          },
          {
            path: 'module/notes',
            element: <NotesPage />,
          },
          {
            path: 'module/notes/create',
            element: <NoteCreatePage />,
          },
          {
            path: 'module/notes/:noteId',
            element: <NoteDetailsPage />,
          },
          {
            path: 'module/notes/:noteId/edit',
            element: <NoteEditPage />,
          },
          {
            path: 'modules/accounts-user-permissions',
            element: <AccountsUserPermissions />,
          },
          {
            path: 'organization',
            element: <OrganizationPage />,
          },
          {
            path: 'organization/update',
            element: <OrganizationUpdatePage />,
          },
          {
            path: 'client-surveys',
            element: <ClientSurveys />,
          },
        ],
      },
    ],
  },
  {
    path: '/admin',
    element: <AdminLayout />,
    children: [
      {
        path: 'dashboard',
        element: <AdminDashboardPage />,
      },
    ],
  },
  {
    path: '/admin/signin',
    element: <AdminSigninPage />,
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'signup',
        element: <SignupPage />,
      },
      {
        path: 'forgot-password',
        element: <ForgotPasswordPage />,
      },
    ],
  },
  // Reset password as standalone route (not under AuthLayout)
  {
    path: '/auth/reset-password',
    element: <ResetPasswordPage />,
  },
  // Accept invite route (standalone, not under any layout)
  {
    path: '/invite/accept',
    element: <AcceptInvitePage />,
  },
  // Organization creation route
  {
    path: '/organization/create',
    element: <CreateOrganizationPage />,
  },

  //testUI
  {
    path: '/testUI',
    element: <Outlet/>,
    children: [
      {
        index: true,
        element: <SignInPage/>
      },
      {
        path: 'reset-password',
        element: <ResetPasswordDialog/>
      },
      {
        path: 'set-new-password',
        element: <SetNewPassword/>
      },
      {
        path: 'create-organization',
        element: <CreateOrganization/>
      },
      {
        path: 'organization-details',
        element: <OrganizationDetailsView/>
      },
      {
        path: 'organization-edit',
        element: <EditOrganizationDetails/>
      },
      {
        path: 'my-account',
        element: <Dashboard/>
      },
      {
        path: 'create-account',
        element: <CreateAccountModal/>
      },
      {
        path: 'my-account-overview',
        element: <AccountOverview/>
      },
      {
        path: 'my-account-overview-edit',
        element: <AccountOverviewEdit/>
      },
      {
        path: 'my-account-contact',
        element: <AccountContact/>
      },
      {
        path: 'my-account-performance',
        element: <PastPerformance/>
      },
      {
        path: 'my-account-notes',
        element: <MyAccountNotes/>
      },
      {
        path: 'my-account-finance',
        element: <MyAccountFinancial/>
      },
      {
        path: 'my-account-opportunities',
        element: <MyOpportunities/>
      }

    ]
  }
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
