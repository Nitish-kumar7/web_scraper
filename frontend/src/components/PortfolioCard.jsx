import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Stack, 
  Divider,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar
} from '@mui/material';
import { 
  Work as WorkIcon,
  Code as CodeIcon,
  School as SchoolIcon,
  Email as EmailIcon,
  LinkedIn as LinkedInIcon,
  GitHub as GitHubIcon,
  Language as LanguageIcon,
  Link as LinkIcon,
  Star as StarIcon
} from '@mui/icons-material';

const PortfolioCard = ({ data }) => {
  if (!data || data.error) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column', maxWidth: '100%' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center', maxWidth: '100%', wordBreak: 'break-word', overflowX: 'hidden', p: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <WorkIcon sx={{ fontSize: 40, color: 'text.secondary', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">Portfolio</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {data?.error || 'No portfolio data found'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getContactIcon = (type) => {
    switch (type) {
      case 'email': return <EmailIcon />;
      case 'linkedin': return <LinkedInIcon />;
      case 'github': return <GitHubIcon />;
      case 'website': return <LanguageIcon />;
      default: return <LinkIcon />;
    }
  };

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
              bgcolor: 'primary.main',
              color: 'white'
            }}
          >
            <WorkIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              {data.name || 'Portfolio'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Professional Portfolio
            </Typography>
          </Box>
        </Box>

        {/* About */}
        {data.about && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              {data.about}
            </Typography>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Skills */}
        {data.skills && data.skills.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
              <CodeIcon sx={{ fontSize: 16 }} />
              Skills & Technologies
            </Typography>
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

        {/* Projects */}
        {data.projects && data.projects.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
              <StarIcon sx={{ fontSize: 16 }} />
              Featured Projects
            </Typography>
            <List dense>
              {data.projects.slice(0, 3).map((project, idx) => (
                <ListItem key={idx} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <LanguageIcon sx={{ fontSize: 16 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={project.title || `Project ${idx + 1}`}
                    secondary={project.description}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                  {project.link && (
                    <Tooltip title="View Project">
                      <IconButton 
                        size="small"
                        onClick={() => window.open(project.link, '_blank')}
                      >
                        <LinkIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Education */}
        {data.education && data.education.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
              <SchoolIcon sx={{ fontSize: 16 }} />
              Education
            </Typography>
            <List dense>
              {data.education.slice(0, 2).map((edu, idx) => (
                <ListItem key={idx} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <SchoolIcon sx={{ fontSize: 16 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={edu}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Experience */}
        {data.experience && data.experience.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
              <WorkIcon sx={{ fontSize: 16 }} />
              Experience
            </Typography>
            <List dense>
              {data.experience.slice(0, 2).map((exp, idx) => (
                <ListItem key={idx} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <WorkIcon sx={{ fontSize: 16 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={exp}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Contact Information */}
        {data.contact && Object.keys(data.contact).length > 0 && (
          <Box>
            <Typography variant="subtitle2" mb={1}>Contact</Typography>
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {Object.entries(data.contact).map(([type, value]) => (
                <Tooltip key={type} title={`View ${type}`}>
                  <IconButton
                    size="small"
                    onClick={() => window.open(value, '_blank')}
                    sx={{ 
                      bgcolor: 'grey.100',
                      '&:hover': { bgcolor: 'grey.200' }
                    }}
                  >
                    {getContactIcon(type)}
                  </IconButton>
                </Tooltip>
              ))}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default PortfolioCard; 