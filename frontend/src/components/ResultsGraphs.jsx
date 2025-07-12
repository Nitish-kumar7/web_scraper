import React from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Bar, Pie, Doughnut, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
);

const ResultsGraphs = ({ results }) => {
  // Certificate validation pie chart
  const certificateData = {
    labels: ['Valid', 'Invalid', 'Expired'],
    datasets: [
      {
        data: [
          results.certificate_summary?.valid_certificates || 0,
          results.certificate_summary?.invalid_certificates || 0,
          Object.values(results.certificates || {}).filter(cert => cert.status === 'Expired').length
        ],
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',
          'rgba(244, 67, 54, 0.8)',
          'rgba(255, 152, 0, 0.8)'
        ],
        borderColor: [
          'rgba(76, 175, 80, 1)',
          'rgba(244, 67, 54, 1)',
          'rgba(255, 152, 0, 1)'
        ],
        borderWidth: 2,
      },
    ],
  };

  // GitHub languages bar chart
  const githubLanguages = results.github_profile?.repositories?.reduce((acc, repo) => {
    if (repo.language) {
      acc[repo.language] = (acc[repo.language] || 0) + 1;
    }
    return acc;
  }, {}) || {};

  const languageData = {
    labels: Object.keys(githubLanguages).slice(0, 8),
    datasets: [
      {
        label: 'Number of Repositories',
        data: Object.values(githubLanguages).slice(0, 8),
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Certificate platforms distribution
  const platformData = {
    labels: Object.keys(
      Object.values(results.certificates || {}).reduce((acc, cert) => {
        const platform = cert.data?.platform || 'Unknown';
        acc[platform] = (acc[platform] || 0) + 1;
        return acc;
      }, {})
    ),
    datasets: [
      {
        data: Object.values(
          Object.values(results.certificates || {}).reduce((acc, cert) => {
            const platform = cert.data?.platform || 'Unknown';
            acc[platform] = (acc[platform] || 0) + 1;
            return acc;
          }, {})
        ),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // GitHub activity line chart (simulated)
  const activityData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Commits',
        data: [12, 19, 3, 5, 2, 3],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  const barOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <Grid container spacing={3}>
      {/* Certificate Validation Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Certificate Validation Status
            </Typography>
            <Box sx={{ height: 300 }}>
              <Pie data={certificateData} options={chartOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* GitHub Languages Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Programming Languages
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar data={languageData} options={barOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Certificate Platforms Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Certificate Platforms Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <Doughnut data={platformData} options={chartOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* GitHub Activity Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              GitHub Activity (Last 6 Months)
            </Typography>
            <Box sx={{ height: 300 }}>
              <Line data={activityData} options={chartOptions} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Summary Stats */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary" fontWeight={600}>
                    {results.certificate_summary?.total_certificates || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Certificates
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main" fontWeight={600}>
                    {results.github_profile?.public_repos || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    GitHub Repositories
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="secondary.main" fontWeight={600}>
                    {results.instagram_profile?.followers || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Instagram Followers
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main" fontWeight={600}>
                    {results.portfolio_data?.skills?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Skills Listed
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ResultsGraphs; 