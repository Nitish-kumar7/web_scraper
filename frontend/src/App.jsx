import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Tabs,
  Tab,
  Button,
  TextField,
  Paper,
  CircularProgress,
  Grid,
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  IconButton,
  Alert,
  Fade,
  Zoom,
  Modal
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  Search as SearchIcon,
  Analytics as AnalyticsIcon,
  GitHub as GitHubIcon,
  Instagram as InstagramIcon,
  Work as WorkIcon,
  Verified as VerifiedIcon,
  LinkedIn as LinkedInIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import GitHubCard from './components/GitHubCard';
import InstagramCard from './components/InstagramCard';
import PortfolioCard from './components/PortfolioCard';
import CertificatesCard from './components/CertificatesCard';
import ResultsGraphs from './components/ResultsGraphs';
import LinkedInCard from './components/LinkedInCard';
import axios from 'axios';

// Import Google Fonts in the document head
if (typeof document !== 'undefined') {
  const link = document.createElement('link');
  link.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap';
  link.rel = 'stylesheet';
  document.head.appendChild(link);
}

// Vibrant Gen Z gradient theme with glassmorphism
const theme = createTheme({
  palette: {
    primary: {
      main: '#7f5af0', // Vibrant purple
      light: '#f15bb5', // Pink
      dark: '#00cfff', // Blue
      contrastText: '#fff',
    },
    secondary: {
      main: '#f15bb5', // Pink
      contrastText: '#fff',
    },
    background: {
      default: 'linear-gradient(120deg, #7f5af0 0%, #f15bb5 50%, #00cfff 100%)',
      paper: 'rgba(255,255,255,0.75)',
    },
    success: { main: '#22c55e' },
    warning: { main: '#f59e42' },
    error: { main: '#ef4444' },
  },
  typography: {
    fontFamily: 'Montserrat, Arial, sans-serif',
    h2: { fontWeight: 900, letterSpacing: 1, fontSize: '3rem', textShadow: '0 4px 24px rgba(127,90,240,0.10)' },
    h5: { fontWeight: 700, letterSpacing: 0.5 },
    h6: { fontWeight: 600 },
    body1: { fontWeight: 500 },
    body2: { fontWeight: 400 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 8px 32px rgba(127,90,240,0.12)',
          borderRadius: 22,
          backdropFilter: 'blur(12px)',
          background: 'rgba(255,255,255,0.75)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 18,
          transition: 'transform 0.2s, box-shadow 0.2s',
          background: 'rgba(255,255,255,0.85)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(241,91,181,0.10)',
          '&:hover': {
            transform: 'translateY(-2px) scale(1.01)',
            boxShadow: '0 12px 40px rgba(0,207,255,0.18)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          fontWeight: 800,
          borderRadius: 12,
          letterSpacing: 1,
        },
      },
    },
  },
});

const DATA_SOURCES = [
  { key: 'github', label: 'GitHub', icon: <GitHubIcon fontSize="large" /> },
  { key: 'instagram', label: 'Instagram', icon: <InstagramIcon fontSize="large" /> },
  { key: 'portfolio', label: 'Portfolio', icon: <WorkIcon fontSize="large" /> },
  { key: 'certificates', label: 'Certificates', icon: <VerifiedIcon fontSize="large" /> },
  { key: 'linkedin', label: 'LinkedIn', icon: <LinkedInIcon fontSize="large" /> },
];

function App() {
  const [tab, setTab] = useState(0);
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [streamingProgress, setStreamingProgress] = useState('');
  const [streamingResults, setStreamingResults] = useState({
    elements: null,
    instagram_profile: null,
    portfolio_data: null,
    github_profile: null,
    certificates: {},
    certificate_summary: null,
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedSource, setSelectedSource] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setError('');
    setResults(null);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setResults(null);
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    setError('');
    setResults(null);
  };

  const handleScrape = async () => {
    setLoading(true);
    setError('');
    setResults(null);
    setStreamingProgress('');
    setStreamingResults({
      elements: null,
      instagram_profile: null,
      portfolio_data: null,
      github_profile: null,
      certificates: {},
      certificate_summary: null,
    });
    setIsStreaming(true);
    
    try {
      if (tab === 0 && file) {
        // Use streaming endpoint
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('http://localhost:8000/upload/stream/', {
          method: 'POST',
          headers: {
            'access_token': 'qFvFLN4VeYm3XqxnY0s8p-6isd5FCSF8o5aeuxhyOuw',
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                switch (data.type) {
                  case 'status':
                    setStreamingProgress(data.message);
                    break;
                  case 'elements':
                    setStreamingResults(prev => ({ ...prev, elements: data.data }));
                    break;
                  case 'instagram':
                    setStreamingResults(prev => ({ ...prev, instagram_profile: data.data }));
                    break;
                  case 'portfolio':
                    setStreamingResults(prev => ({ ...prev, portfolio_data: data.data }));
                    break;
                  case 'github':
                    setStreamingResults(prev => ({ ...prev, github_profile: data.data }));
                    break;
                  case 'certificate_progress':
                    setStreamingResults(prev => ({
                      ...prev,
                      certificates: { ...prev.certificates, [data.url]: data.data }
                    }));
                    break;
                  case 'complete':
                    setResults(data.data);
                    setIsStreaming(false);
                    setLoading(false);
                    return;
                  case 'error':
                    setError(data.message);
                    setIsStreaming(false);
                    setLoading(false);
                    return;
                }
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError);
              }
            }
          }
        }
      } else if (tab === 1 && text.trim()) {
        setError('Text input feature requires backend modification. Please use file upload for now.');
        setLoading(false);
        setIsStreaming(false);
        return;
      } else {
        setError('Please provide a file or text input.');
        setLoading(false);
        setIsStreaming(false);
        return;
      }
    } catch (err) {
      setError('Failed to scrape. Please check your backend connection and try again.');
      setIsStreaming(false);
      setLoading(false);
    }
  };

  // Set default selected source after results are available
  React.useEffect(() => {
    if (results || isStreaming) {
      const available = DATA_SOURCES.find(ds => {
        if (results) {
          if (ds.key === 'github' && results.github_profile) return true;
          if (ds.key === 'instagram' && results.instagram_profile) return true;
          if (ds.key === 'portfolio' && results.portfolio_data) return true;
          if (ds.key === 'certificates' && results.certificates && Object.keys(results.certificates).length > 0) return true;
          if (ds.key === 'linkedin' && results.linkedin_profile) return true;
        } else if (isStreaming) {
          if (ds.key === 'github' && streamingResults.github_profile) return true;
          if (ds.key === 'instagram' && streamingResults.instagram_profile) return true;
          if (ds.key === 'portfolio' && streamingResults.portfolio_data) return true;
          if (ds.key === 'certificates' && streamingResults.certificates && Object.keys(streamingResults.certificates).length > 0) return true;
          if (ds.key === 'linkedin' && streamingResults.linkedin_profile) return true;
        }
        return false;
      });
      if (available) setSelectedSource(available.key);
    } else {
      setSelectedSource('');
    }
  }, [results, isStreaming, streamingResults]);

  // When a new analysis completes, add it to history
  React.useEffect(() => {
    if (results && !isStreaming) {
      setHistory(prev => [
        {
          timestamp: new Date().toLocaleString(),
          results,
          summary: {
            github: !!results.github_profile,
            instagram: !!results.instagram_profile,
            portfolio: !!results.portfolio_data,
            certificates: results.certificates && Object.keys(results.certificates).length > 0
          }
        },
        ...prev
      ]);
    }
  }, [results, isStreaming]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* History Drawer/Panel */}
      {showHistory && (
        <Paper sx={{ position: 'fixed', top: 90, right: 32, width: 340, maxHeight: '80vh', overflowY: 'auto', zIndex: 2500, p: 2, borderRadius: 4, boxShadow: '0 8px 32px rgba(127,90,240,0.18)', background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(10px)' }}>
          <Typography variant="h6" sx={{ fontWeight: 900, mb: 2, fontFamily: 'Montserrat', color: '#7f5af0' }}>Analysis History</Typography>
          {history.length === 0 && <Typography color="text.secondary">No history yet.</Typography>}
          {history.map((item, idx) => (
            <Paper key={idx} sx={{ mb: 2, p: 2, cursor: 'pointer', border: '2px solid #f15bb5', borderRadius: 2, background: 'rgba(241,91,181,0.08)' }} onClick={() => { setResults(item.results); setShowHistory(false); }}>
              <Typography variant="body2" sx={{ fontWeight: 700 }}>{item.timestamp}</Typography>
              <Box display="flex" gap={1} mt={1}>
                {item.summary.github && <GitHubIcon color="primary" />}
                {item.summary.instagram && <InstagramIcon color="secondary" />}
                {item.summary.portfolio && <WorkIcon color="action" />}
                {item.summary.certificates && <VerifiedIcon color="success" />}
              </Box>
            </Paper>
          ))}
        </Paper>
      )}
      {/* App Bar */}
      <AppBar position="absolute" elevation={0} sx={{ bgcolor: 'primary.main', width: '100vw', left: 0, top: 0, zIndex: 1200 }}>
        <Toolbar>
          <SearchIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 900, fontFamily: 'Montserrat', color: '#fff', letterSpacing: 2 }}>
            Smart Web Scraper
          </Typography>
          <IconButton color="inherit" size="large">
            <AnalyticsIcon />
          </IconButton>
          <IconButton
            onClick={() => setShowHistory(h => !h)}
            sx={{
              ml: 2,
              bgcolor: 'rgba(255,255,255,0.18)',
              color: '#fff',
              borderRadius: 2,
              boxShadow: '0 4px 32px 0 rgba(127,90,240,0.18)',
              backdropFilter: 'blur(8px)',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: 'rgba(241,91,181,0.22)',
                color: '#f15bb5',
                boxShadow: '0 8px 40px 0 rgba(241,91,181,0.18)',
              },
            }}
            aria-label="Show History"
          >
            <AccessTimeIcon sx={{ fontSize: 32 }} />
          </IconButton>
        </Toolbar>
      </AppBar>
      {/* Main Content Centered */}
      <Box
        sx={{
          flex: 1,
          width: '100vw',
          minHeight: '100vh',
          background: 'linear-gradient(120deg, #7f5af0 0%, #f15bb5 50%, #00cfff 100%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Hero Section */}
        <Box textAlign="center" mb={4}>
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 900,
              color: '#fff',
              letterSpacing: 2,
              textShadow: '0 6px 32px rgba(127,90,240,0.18), 0 2px 8px #f15bb5',
              fontFamily: 'Montserrat',
              fontSize: { xs: '2.2rem', sm: '3rem', md: '3.5rem' },
            }}
          >
            Smart Web Scraper
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 600,
              mx: 'auto',
              color: '#f3f4f6',
              fontWeight: 500,
              fontFamily: 'Montserrat',
              fontSize: { xs: '1rem', sm: '1.2rem' },
              textShadow: '0 2px 8px #7f5af0',
            }}
          >
            Extract and validate portfolio, certificate, and social data from DOCX files or text. Supports GitHub, Instagram, LinkedIn, Coursera, Udemy, Credly, EdX, and more!
          </Typography>
        </Box>
          {/* Input Section - Centered Card */}
          <Paper
            sx={{
              p: 4,
              mb: 4,
              width: '100%',
              maxWidth: 480,
              mx: 'auto',
              borderRadius: 4,
              boxShadow: '0 8px 32px rgba(37,99,235,0.18)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: 'rgba(255,255,255,0.98)',
            }}
          >
            <Box display="flex" alignItems="center" mb={3} width="100%">
              <DescriptionIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Typography variant="h5" component="h2" sx={{ fontWeight: 700, fontFamily: 'Montserrat' }}>
                Input Source
              </Typography>
            </Box>

            <Tabs
              value={tab}
              onChange={handleTabChange}
              centered
              sx={{
                mb: 3,
                width: '100%',
                '& .MuiTab-root': {
                  minHeight: 64,
                  fontSize: '1rem',
                  fontWeight: 700,
                  fontFamily: 'Montserrat',
                },
                '& .MuiTabs-indicator': {
                  background: 'linear-gradient(90deg, #2563eb 0%, #ec4899 100%)',
                  height: 4,
                  borderRadius: 2,
                },
              }}
            >
              <Tab
                label="Upload Document"
                icon={<CloudUploadIcon />}
                iconPosition="start"
              />
              <Tab
                label="Paste Text"
                icon={<DescriptionIcon />}
                iconPosition="start"
              />
            </Tabs>

            <Fade in={true} timeout={500}>
              <Box width="100%">
                {tab === 0 && (
                  <Box textAlign="center">
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUploadIcon />}
                      sx={{
                        mb: 2,
                        py: 2,
                        px: 4,
                        fontSize: '1.1rem',
                        borderWidth: 2,
                        color: 'primary.main',
                        borderColor: 'primary.main',
                        fontFamily: 'Montserrat',
                        fontWeight: 700,
                        '&:hover': {
                          borderWidth: 2,
                          background: 'linear-gradient(90deg, #60a5fa 0%, #ec4899 100%)',
                          color: '#fff',
                        },
                      }}
                    >
                      Choose DOCX File
                      <input type="file" hidden accept=".docx" onChange={handleFileChange} />
                    </Button>
                    {file && (
                      <Alert severity="success" sx={{ maxWidth: 400, mx: 'auto', fontFamily: 'Montserrat' }}>
                        Selected: {file.name}
                      </Alert>
                    )}
                  </Box>
                )}

                {tab === 1 && (
                  <TextField
                    label="Paste your content here"
                    multiline
                    minRows={8}
                    fullWidth
                    value={text}
                    onChange={handleTextChange}
                    variant="outlined"
                    placeholder="Paste your resume, portfolio text, or any content containing links and information..."
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        fontSize: '1rem',
                        fontFamily: 'Montserrat',
                      },
                    }}
                  />
                )}

                <Box textAlign="center" mt={3}>
                  <LoadingButton
                    variant="contained"
                    color="primary"
                    onClick={handleScrape}
                    loading={loading}
                    disabled={loading || (tab === 0 && !file) || (tab === 1 && !text.trim())}
                    size="large"
                    startIcon={<SearchIcon />}
                    sx={{
                      py: 1.5,
                      px: 4,
                      fontSize: '1.1rem',
                      fontWeight: 900,
                      borderRadius: 2,
                      minWidth: 220,
                      boxShadow: '0 2px 8px rgba(37,99,235,0.10)',
                      background: 'linear-gradient(90deg, #2563eb 0%, #ec4899 100%)',
                      color: '#fff',
                      fontFamily: 'Montserrat',
                      '&:hover': {
                        background: 'linear-gradient(90deg, #ec4899 0%, #2563eb 100%)',
                        color: '#fff',
                      },
                      opacity: loading || (tab === 0 && !file) || (tab === 1 && !text.trim()) ? 0.6 : 1,
                    }}
                  >
                    {loading ? 'Scraping...' : 'Analyze Content'}
                  </LoadingButton>
                </Box>

                {error && (
                  <Fade in={true}>
                    <Alert severity="error" sx={{ mt: 2, maxWidth: 600, mx: 'auto', fontFamily: 'Montserrat' }}>
                      {error}
                    </Alert>
                  </Fade>
                )}

                {/* Streaming Progress */}
                {isStreaming && streamingProgress && (
                  <Fade in={true}>
                    <Alert severity="info" sx={{ mt: 2, maxWidth: 600, mx: 'auto', fontFamily: 'Montserrat' }}>
                      <Box display="flex" alignItems="center">
                        <CircularProgress size={20} sx={{ mr: 2 }} />
                        {streamingProgress}
                      </Box>
                    </Alert>
                  </Fade>
                )}
              </Box>
            </Fade>
          </Paper>

          {/* Results Section */}
          {(results || isStreaming) && (
            <Zoom in={true} timeout={800}>
              <Box width="100%">
                {/* Icon Selector Row */}
                <Box display="flex" justifyContent="center" alignItems="center" gap={4} mb={3}>
                  {DATA_SOURCES.map(ds => {
                    const isAvailable = results
                      ? (ds.key === 'github' && results.github_profile) ||
                        (ds.key === 'instagram' && results.instagram_profile) ||
                        (ds.key === 'portfolio' && results.portfolio_data) ||
                        (ds.key === 'certificates' && results.certificates && Object.keys(results.certificates).length > 0) ||
                        (ds.key === 'linkedin' && results.linkedin_profile)
                      : (ds.key === 'github' && streamingResults.github_profile) ||
                        (ds.key === 'instagram' && streamingResults.instagram_profile) ||
                        (ds.key === 'portfolio' && streamingResults.portfolio_data) ||
                        (ds.key === 'certificates' && streamingResults.certificates && Object.keys(streamingResults.certificates).length > 0) ||
                        (ds.key === 'linkedin' && streamingResults.linkedin_profile);
                    return (
                      <Box
                        key={ds.key}
                        onClick={() => isAvailable && setSelectedSource(ds.key)}
                        sx={{
                          cursor: isAvailable ? 'pointer' : 'not-allowed',
                          opacity: isAvailable ? 1 : 0.3,
                          borderBottom: selectedSource === ds.key ? '4px solid #ec4899' : '4px solid transparent',
                          transition: 'border-bottom 0.2s',
                          px: 2,
                          py: 1,
                          borderRadius: 2,
                          bgcolor: selectedSource === ds.key ? 'background.paper' : 'transparent',
                          boxShadow: selectedSource === ds.key ? '0 2px 8px rgba(236,72,153,0.10)' : 'none',
                        }}
                      >
                        {ds.icon}
                        <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontWeight: 600, fontFamily: 'Montserrat' }}>{ds.label}</Typography>
                      </Box>
                    );
                  })}
                </Box>

                {/* Focused Card Display as Modal */}
                <Modal
                  open={!!selectedSource}
                  onClose={() => setSelectedSource('')}
                  aria-labelledby="data-source-modal"
                  sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}
                >
                  <Box
                    sx={{
                      outline: 'none',
                      bgcolor: 'background.paper',
                      borderRadius: 4,
                      boxShadow: 24,
                      p: 3,
                      minWidth: { xs: '90vw', sm: 500 },
                      maxWidth: '95vw',
                      maxHeight: '90vh',
                      overflowY: 'auto',
                      position: 'relative',
                    }}
                  >
                    {/* Close Button */}
                    <IconButton
                      onClick={() => setSelectedSource('')}
                      sx={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}
                      aria-label="close"
                    >
                      <span style={{ fontSize: 24, fontWeight: 900 }}>&times;</span>
                    </IconButton>
                    {selectedSource === 'github' && (
                      <GitHubCard
                        data={results?.github_profile || streamingResults.github_profile}
                        isLoading={isStreaming && !streamingResults.github_profile}
                      />
                    )}
                    {selectedSource === 'instagram' && (
                      <InstagramCard
                        data={results?.instagram_profile || streamingResults.instagram_profile}
                        isLoading={isStreaming && !streamingResults.instagram_profile}
                        popupStyle // pass a prop to trigger Instagram page-like style
                      />
                    )}
                    {selectedSource === 'portfolio' && (
                      <PortfolioCard
                        data={results?.portfolio_data || streamingResults.portfolio_data}
                        isLoading={isStreaming && !streamingResults.portfolio_data}
                      />
                    )}
                    {selectedSource === 'certificates' && (
                      <CertificatesCard
                        data={results?.certificates || streamingResults.certificates}
                        summary={results?.certificate_summary || streamingResults.certificate_summary}
                        isLoading={isStreaming}
                      />
                    )}
                    {selectedSource === 'linkedin' && (
                      <LinkedInCard
                        data={results?.linkedin_profile || streamingResults.linkedin_profile}
                        isLoading={isStreaming && !streamingResults.linkedin_profile}
                      />
                    )}
                  </Box>
                </Modal>
              </Box>
            </Zoom>
          )}
        </Box>
    </ThemeProvider>
  );
}

export default App;
