import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import ConceptsPage from './pages/ConceptsPage';
import WorldSettingsPage from './pages/WorldSettingsPage';
import PlotOutlinesPage from './pages/PlotOutlinesPage';
import CharactersPage from './pages/CharactersPage';
import CharacterDetailPage from './pages/CharacterDetailPage';
import ChaptersPage from './pages/ChaptersPage';
import ChapterDetailPage from './pages/ChapterDetailPage';
import SettingsPage from './pages/SettingsPage';
import NotFoundPage from './pages/NotFoundPage';
import ErrorBoundary from './components/ErrorBoundary';
import { Toaster } from 'react-hot-toast';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="projects/:projectId/concepts" element={<ConceptsPage />} />
            <Route path="projects/:projectId/world-settings" element={<WorldSettingsPage />} />
            <Route path="projects/:projectId/plot-outlines" element={<PlotOutlinesPage />} />
            <Route path="projects/:projectId/characters" element={<CharactersPage />} />
            <Route path="projects/:projectId/characters/:characterId" element={<CharacterDetailPage />} />
            <Route path="projects/:projectId/chapters" element={<ChaptersPage />} />
            <Route path="projects/:projectId/chapters/:chapterId" element={<ChapterDetailPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
