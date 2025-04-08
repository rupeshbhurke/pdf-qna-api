import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch existing files and QA history on component mount
  useEffect(() => {
    fetchFiles();
    fetchQAHistory();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files`);
      setFiles(response.data.files);
    } catch (err) {
      setError('Failed to fetch existing files');
    }
  };

  const fetchQAHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/qa-history`);
      setQaHistory(response.data.history);
    } catch (err) {
      setError('Failed to fetch QA history');
    }
  };

  const handleFileChange = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    if (selectedFiles.length === 0) return;

    setLoading(true);
    setError('');

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await fetchFiles();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload files');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async (filename) => {
    try {
      await axios.delete(`${API_BASE_URL}/files/${filename}`);
      await fetchFiles();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete file');
    }
  };

  const handleClearHistory = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/qa-history`);
      setQaHistory([]);
    } catch (err) {
      setError('Failed to clear history');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!question) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError('');
    setAnswer('');

    const formData = new FormData();
    formData.append('question', question);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnswer(response.data.answer);
      await fetchQAHistory(); // Refresh QA history
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          PDF Q&A System
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
              fullWidth
            >
              Upload PDFs
              <input
                type="file"
                hidden
                multiple
                accept=".pdf"
                onChange={handleFileChange}
              />
            </Button>
          </Box>

          {files.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Uploaded Files
              </Typography>
              <List>
                {files.map((file, index) => (
                  <React.Fragment key={file.filename}>
                    <ListItem>
                      <ListItemText primary={file.filename} />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          aria-label="delete"
                          onClick={() => handleDeleteFile(file.filename)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < files.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Your Question"
              variant="outlined"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              sx={{ mb: 3 }}
            />

            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={loading || files.length === 0}
            >
              {loading ? <CircularProgress size={24} /> : 'Get Answer'}
            </Button>
          </form>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {answer && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Answer:
              </Typography>
              <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography>{answer}</Typography>
              </Paper>
            </Box>
          )}

          {qaHistory.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Question & Answer History</Typography>
                <Button
                  variant="outlined"
                  color="secondary"
                  size="small"
                  onClick={handleClearHistory}
                >
                  Clear History
                </Button>
              </Box>
              {qaHistory.map((record) => (
                <Accordion key={record.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>{record.question}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {formatDate(record.timestamp)}
                    </Typography>
                    <Typography paragraph>{record.answer}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Source Files: {record.source_files.join(', ')}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
}

export default App; 