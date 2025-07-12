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
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  LinkedIn as LinkedInIcon,
  Work as WorkIcon,
  School as SchoolIcon,
  LocationOn as LocationIcon,
  Link as LinkIcon,
  People as PeopleIcon,
  Star as StarIcon
} from '@mui/icons-material';

const LinkedInCard = ({ data, isLoading = false }) => {
  if (isLoading) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <LinkedInIcon sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">LinkedIn</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Fetching LinkedIn profile...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.error) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <LinkedInIcon sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">LinkedIn</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {data?.error || 'No LinkedIn data found'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="outlined" sx={{ maxWidth: 480, width: '100%', borderRadius: 4, boxShadow: 8, p: 0, overflow: 'visible', bgcolor: 'background.paper' }}>
      <CardContent sx={{ p: 3, pb: 2 }}>
        {/* Profile Header */}
        <Box display="flex" alignItems="center" gap={3} mb={2}>
          <Avatar
            src={data.profile_pic_url}
            sx={{ width: 80, height: 80, border: '3px solid #0a66c2', boxShadow: '0 2px 12px #0a66c233' }}
          >
            <LinkedInIcon fontSize="large" />
          </Avatar>
          <Box flex={1}>
            <Typography variant="h6" fontWeight={700} sx={{ fontFamily: 'Montserrat', letterSpacing: 1 }}>
              {data.name || 'LinkedIn User'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'Montserrat' }}>
              {data.headline || 'Professional'}
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={1}>
              {data.location && (
                <>
                  <LocationIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" color="text.secondary">{data.location}</Typography>
                </>
              )}
            </Box>
          </Box>
          <Tooltip title="View LinkedIn Profile">
            <IconButton
              size="small"
              onClick={() => window.open(data.profile_url, '_blank')}
              sx={{ ml: 'auto', bgcolor: '#0a66c2', color: '#fff', '&:hover': { bgcolor: '#004182' } }}
            >
              <LinkIcon />
            </IconButton>
          </Tooltip>
        </Box>
        {/* Stats */}
        <Box display="flex" gap={2} mb={2}>
          <Chip
            icon={<PeopleIcon />}
            label={`${data.connections || 0} Connections`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
        {/* About */}
        {data.about && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} sx={{ fontFamily: 'Montserrat', fontWeight: 600 }}>About</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'Montserrat' }}>{data.about}</Typography>
          </Box>
        )}
        {/* Experience */}
        {data.experience && data.experience.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} sx={{ fontFamily: 'Montserrat', fontWeight: 600 }}>Experience</Typography>
            <List dense>
              {data.experience.slice(0, 3).map((exp, idx) => (
                <ListItem key={idx} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <WorkIcon sx={{ fontSize: 16 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={exp.title || 'Role'}
                    secondary={exp.company ? `${exp.company} • ${exp.duration || ''}` : ''}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        {/* Education */}
        {data.education && data.education.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} sx={{ fontFamily: 'Montserrat', fontWeight: 600 }}>Education</Typography>
            <List dense>
              {data.education.slice(0, 2).map((edu, idx) => (
                <ListItem key={idx} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <SchoolIcon sx={{ fontSize: 16 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={edu.degree || edu.school || 'Education'}
                    secondary={edu.school && edu.degree ? `${edu.school}` : ''}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        {/* Skills */}
        {data.skills && data.skills.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} sx={{ fontFamily: 'Montserrat', fontWeight: 600 }}>Skills</Typography>
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {data.skills.slice(0, 8).map((skill, idx) => (
                <Chip
                  key={idx}
                  label={skill}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
              {data.skills.length > 8 && (
                <Chip
                  label={`+${data.skills.length - 8} more`}
                  size="small"
                  color="default"
                  variant="outlined"
                />
              )}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default LinkedInCard; 