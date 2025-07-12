import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Avatar,
  Box,
  Chip,
  Stack,
  Divider,
  IconButton,
  Tooltip,
  LinearProgress,
  CircularProgress
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  Star as StarIcon,
  ForkRight as ForkIcon,
  Visibility as EyeIcon,
  Language as LanguageIcon,
  Link as LinkIcon
} from '@mui/icons-material';

const GitHubCard = ({ data, isLoading = false }) => {
  if (isLoading) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <GitHubIcon sx={{ fontSize: 40, color: 'text.secondary', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">GitHub</Typography>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary">
              Fetching GitHub profile...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.error) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <GitHubIcon sx={{ fontSize: 40, color: 'text.secondary', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">GitHub</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {data?.error || 'No GitHub data found'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const topLanguages = data.repositories?.reduce((acc, repo) => {
    if (repo.language) {
      acc[repo.language] = (acc[repo.language] || 0) + 1;
    }
    return acc;
  }, {}) || {};

  const sortedLanguages = Object.entries(topLanguages)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const totalStars = data.repositories?.reduce((sum, repo) => sum + repo.stars, 0) || 0;
  const totalForks = data.repositories?.reduce((sum, repo) => sum + repo.forks, 0) || 0;

  return (
    <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column', maxWidth: '100%' }}>
      <CardContent sx={{ flexGrow: 1, textAlign: 'center', maxWidth: '100%', wordBreak: 'break-word', overflowX: 'hidden', p: 2 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar
            src={data.avatar_url}
            alt={data.username}
            sx={{ width: 56, height: 56, mr: 2 }}
          />
          <Box>
            <Typography variant="h6" fontWeight={600}>
              {data.name || data.username}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              @{data.username}
            </Typography>
          </Box>
          <Tooltip title="View GitHub Profile">
            <IconButton
              size="small"
              sx={{ ml: 'auto' }}
              onClick={() => window.open(`https://github.com/${data.username}`, '_blank')}
            >
              <LinkIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Bio */}
        {data.bio && (
          <Typography variant="body2" color="text.secondary" mb={2}>
            {data.bio}
          </Typography>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Stats */}
        <Box display="flex" justifyContent="space-around" mb={2}>
          <Box textAlign="center">
            <Typography variant="h6" color="primary" fontWeight={600}>
              {data.public_repos || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Repositories
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="h6" color="primary" fontWeight={600}>
              {data.followers || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Followers
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="h6" color="primary" fontWeight={600}>
              {data.following || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Following
            </Typography>
          </Box>
        </Box>

        {/* Repository Stats */}
        <Box mb={2}>
          <Typography variant="subtitle2" mb={1}>Repository Stats</Typography>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <StarIcon sx={{ fontSize: 16, color: 'warning.main' }} />
            <Typography variant="body2">{totalStars} total stars</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <ForkIcon sx={{ fontSize: 16, color: 'info.main' }} />
            <Typography variant="body2">{totalForks} total forks</Typography>
          </Box>
        </Box>

        {/* Top Languages */}
        {sortedLanguages.length > 0 && (
          <Box>
            <Typography variant="subtitle2" mb={1}>Top Languages</Typography>
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {sortedLanguages.map(([lang, count]) => (
                <Chip
                  key={lang}
                  icon={<LanguageIcon />}
                  label={`${lang} (${count})`}
                  size="small"
                  variant="outlined"
                  color="primary"
                />
              ))}
            </Stack>
          </Box>
        )}

        {/* Recent Activity */}
        {data.contributions && (
          <Box mt={2}>
            <Typography variant="subtitle2" mb={1}>Recent Activity</Typography>
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <Typography variant="body2">{data.contributions.commits || 0} commits</Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <Typography variant="body2">{data.contributions.pull_requests || 0} pull requests</Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="body2">{data.contributions.issues || 0} issues</Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default GitHubCard; 