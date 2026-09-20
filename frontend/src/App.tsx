import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import NewApplication from './pages/NewApplication';
import DocumentUpload from './pages/DocumentUpload';
import VerificationProgress from './pages/VerificationProgress';
import VerificationResult from './pages/VerificationResult';
import FindingsEvidence from './pages/FindingsEvidence';
import MyApplications from './pages/MyApplications';

function AppLayout() {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  return (
    <div className={isLanding ? 'landing-layout' : 'app-layout'}>
      {!isLanding && <Sidebar />}
      <main className={isLanding ? 'landing-main' : 'app-main'}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/new" element={<NewApplication />} />
          <Route path="/upload/:sessionId" element={<DocumentUpload />} />
          <Route path="/progress/:sessionId" element={<VerificationProgress />} />
          <Route path="/result/:sessionId" element={<VerificationResult />} />
          <Route path="/findings/:sessionId" element={<FindingsEvidence />} />
          <Route path="/applications" element={<MyApplications />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </AppProvider>
  );
}
