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
  Instagram as InstagramIcon,
  People as PeopleIcon,
  PhotoCamera as PhotoIcon,
  Link as LinkIcon,
  TrendingUp as TrendingIcon
} from '@mui/icons-material';

const InstagramCard = ({ data, isLoading = false, popupStyle = false }) => {
  if (isLoading) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <InstagramIcon sx={{ fontSize: 40, color: 'text.secondary', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">Instagram</Typography>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary">
              Fetching Instagram profile...
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
            <InstagramIcon sx={{ fontSize: 40, color: 'secondary.main', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">Instagram</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {data?.error || 'No Instagram data found'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (popupStyle) {
    // Instagram-like profile layout
    return (
      <Card variant="outlined" sx={{ maxWidth: 420, width: '100%', borderRadius: 4, boxShadow: 8, p: 0, overflow: 'visible', bgcolor: 'background.paper' }}>
        <CardContent sx={{ p: 3, pb: 2 }}>
          {/* Profile Header */}
          <Box display="flex" alignItems="center" gap={3} mb={2}>
            <Avatar
              src={data.profile_pic_url}
              sx={{ width: 80, height: 80, border: '3px solid #e1306c', boxShadow: '0 2px 12px #e1306c33' }}
            >
              <InstagramIcon fontSize="large" />
            </Avatar>
            <Box flex={1}>
              <Typography variant="h6" fontWeight={700} sx={{ fontFamily: 'Montserrat', letterSpacing: 1 }}>
                @{data.username}
              </Typography>
              <Box display="flex" gap={2} mt={1}>
                <Box textAlign="center">
                  <Typography variant="subtitle1" fontWeight={700}>{data.posts_count || 0}</Typography>
                  <Typography variant="caption" color="text.secondary">Posts</Typography>
                </Box>
                <Box textAlign="center">
                  <Typography variant="subtitle1" fontWeight={700}>{data.followers || 0}</Typography>
                  <Typography variant="caption" color="text.secondary">Followers</Typography>
                </Box>
                <Box textAlign="center">
                  <Typography variant="subtitle1" fontWeight={700}>{data.following || 0}</Typography>
                  <Typography variant="caption" color="text.secondary">Following</Typography>
                </Box>
              </Box>
            </Box>
            <Tooltip title="View Instagram Profile">
              <IconButton
                size="small"
                onClick={() => window.open(`https://instagram.com/${data.username}`, '_blank')}
                sx={{ ml: 'auto', bgcolor: '#e1306c', color: '#fff', '&:hover': { bgcolor: '#c13584' } }}
              >
                <LinkIcon />
              </IconButton>
            </Tooltip>
          </Box>
          {/* Bio */}
          {data.bio && (
            <Typography variant="body2" color="text.secondary" mb={2} sx={{ fontFamily: 'Montserrat' }}>
              {data.bio}
            </Typography>
          )}
          {/* Activity/Status */}
          <Box display="flex" gap={2} mb={2}>
            <Chip
              icon={<PhotoIcon />}
              label={data.posts_count > 0 ? "Active" : "Inactive"}
              size="small"
              color={data.posts_count > 0 ? "success" : "default"}
              variant="outlined"
            />
            <Chip
              icon={<PeopleIcon />}
              label={data.followers > 1000 ? "Popular" : "Growing"}
              size="small"
              color={data.followers > 1000 ? "warning" : "info"}
              variant="outlined"
            />
            {data.engagement_rate && (
              <Chip
                icon={<TrendingIcon />}
                label={`Engagement: ${data.engagement_rate}%`}
                size="small"
                color="secondary"
                variant="outlined"
              />
            )}
          </Box>
          {/* Posts Grid */}
          {data.recent_posts && data.recent_posts.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" mb={1} sx={{ fontFamily: 'Montserrat', fontWeight: 600 }}>Recent Posts</Typography>
              <Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={1}>
                {data.recent_posts.slice(0, 6).map((post, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      width: 90,
                      height: 90,
                      borderRadius: 2,
                      overflow: 'hidden',
                      boxShadow: 2,
                      cursor: 'pointer',
                      background: `url(${post.image_url}) center/cover no-repeat`,
                      border: '2px solid #fafafa',
                    }}
                    onClick={() => window.open(post.link, '_blank')}
                  />
                ))}
              </Box>
            </Box>
          )}
          {/* Timestamp */}
          {data.timestamp && (
            <Box mt={2} pt={1} borderTop={1} borderColor="divider">
              <Typography variant="caption" color="text.secondary">
                Last updated: {new Date(data.timestamp).toLocaleDateString()}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  }

  const engagementRate = data.followers ?
    ((data.posts_count || 0) / data.followers * 100).toFixed(2) : 0;

  return (
    <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column', maxWidth: '100%' }}>
      <CardContent sx={{ flexGrow: 1, textAlign: 'center', maxWidth: '100%', wordBreak: 'break-word', overflowX: 'hidden', p: 2 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              mr: 2,
              bgcolor: 'secondary.main',
              color: 'white'
            }}
          >
            <InstagramIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              @{data.username}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Instagram Profile
            </Typography>
          </Box>
          <Tooltip title="View Instagram Profile">
            <IconButton
              size="small"
              sx={{ ml: 'auto' }}
              onClick={() => window.open(`https://instagram.com/${data.username}`, '_blank')}
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
            <Typography variant="h6" color="secondary.main" fontWeight={600}>
              {data.followers?.toLocaleString() || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Followers
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="h6" color="secondary.main" fontWeight={600}>
              {data.following?.toLocaleString() || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Following
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="h6" color="secondary.main" fontWeight={600}>
              {data.posts_count?.toLocaleString() || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Posts
            </Typography>
          </Box>
        </Box>

        {/* Engagement Metrics */}
        <Box mb={2}>
          <Typography variant="subtitle2" mb={1}>Engagement Metrics</Typography>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <PeopleIcon sx={{ fontSize: 16, color: 'info.main' }} />
            <Typography variant="body2">
              Engagement Rate: {engagementRate}%
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <TrendingIcon sx={{ fontSize: 16, color: 'success.main' }} />
            <Typography variant="body2">
              Follower Ratio: {data.followers && data.following ?
                (data.followers / data.following).toFixed(2) : 'N/A'}
            </Typography>
          </Box>
        </Box>

        {/* Activity Level */}
        <Box mb={2}>
          <Typography variant="subtitle2" mb={1}>Activity Level</Typography>
          <LinearProgress
            variant="determinate"
            value={Math.min((data.posts_count || 0) / 100 * 100, 100)}
            sx={{ height: 8, borderRadius: 4 }}
            color="secondary"
          />
          <Typography variant="caption" color="text.secondary">
            {data.posts_count || 0} posts
          </Typography>
        </Box>

        {/* Profile Status */}
        <Box>
          <Typography variant="subtitle2" mb={1}>Profile Status</Typography>
          <Stack direction="row" spacing={1}>
            <Chip
              icon={<PhotoIcon />}
              label={data.posts_count > 0 ? "Active" : "Inactive"}
              size="small"
              color={data.posts_count > 0 ? "success" : "default"}
              variant="outlined"
            />
            <Chip
              icon={<PeopleIcon />}
              label={data.followers > 1000 ? "Popular" : "Growing"}
              size="small"
              color={data.followers > 1000 ? "warning" : "info"}
              variant="outlined"
            />
          </Stack>
        </Box>

        {/* Timestamp */}
        {data.timestamp && (
          <Box mt={2} pt={1} borderTop={1} borderColor="divider">
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(data.timestamp).toLocaleDateString()}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default InstagramCard; 