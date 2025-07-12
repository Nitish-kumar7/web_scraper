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
  Avatar,
  LinearProgress
} from '@mui/material';
import { 
  Verified as VerifiedIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  School as SchoolIcon,
  Link as LinkIcon,
  TrendingUp as TrendingIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const CertificatesCard = ({ data, summary }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column', maxWidth: '100%' }}>
        <CardContent sx={{ flexGrow: 1, textAlign: 'center', maxWidth: '100%', wordBreak: 'break-word', overflowX: 'hidden', p: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
            <VerifiedIcon sx={{ fontSize: 40, color: 'text.secondary', mr: 1 }} />
            <Typography variant="h6" color="text.secondary">Certificates</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            No certificates found
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Valid': return <CheckCircleIcon color="success" />;
      case 'Invalid': return <CancelIcon color="error" />;
      case 'Expired': return <WarningIcon color="warning" />;
      default: return <WarningIcon color="default" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Valid': return 'success';
      case 'Invalid': return 'error';
      case 'Expired': return 'warning';
      default: return 'default';
    }
  };

  const certificates = Object.entries(data);
  const validCount = certificates.filter(([, cert]) => cert.status === 'Valid').length;
  const invalidCount = certificates.filter(([, cert]) => cert.status === 'Invalid').length;
  const expiredCount = certificates.filter(([, cert]) => cert.status === 'Expired').length;

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
              bgcolor: 'success.main',
              color: 'white'
            }}
          >
            <VerifiedIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Certificates
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Validation Results
            </Typography>
          </Box>
        </Box>

        {/* Summary Stats */}
        {summary && (
          <Box mb={2}>
            <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
              <AssessmentIcon sx={{ fontSize: 16 }} />
              Validation Summary
            </Typography>
            <Box display="flex" justifyContent="space-around" mb={2}>
              <Box textAlign="center">
                <Typography variant="h6" color="success.main" fontWeight={600}>
                  {summary.valid_certificates || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Valid
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="h6" color="error.main" fontWeight={600}>
                  {summary.invalid_certificates || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Invalid
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="h6" color="warning.main" fontWeight={600}>
                  {expiredCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Expired
                </Typography>
              </Box>
            </Box>
            
            {/* Validation Rate */}
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="caption">Validation Rate</Typography>
                <Typography variant="caption" fontWeight={600}>
                  {summary.validation_rate || 0}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={summary.validation_rate || 0}
                sx={{ height: 8, borderRadius: 4 }}
                color={summary.validation_rate >= 80 ? "success" : summary.validation_rate >= 50 ? "warning" : "error"}
              />
            </Box>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Certificate List */}
        <Box>
          <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
            <SchoolIcon sx={{ fontSize: 16 }} />
            Certificate Details
          </Typography>
          <List dense>
            {certificates.slice(0, 4).map(([url, cert], idx) => (
              <ListItem key={idx} sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  {getStatusIcon(cert.status)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight={500}>
                        {cert.data?.platform || 'Unknown Platform'}
                      </Typography>
                      <Chip
                        label={cert.status}
                        size="small"
                        color={getStatusColor(cert.status)}
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      {cert.data?.name && (
                        <Typography variant="caption" display="block">
                          {cert.data.name}
                        </Typography>
                      )}
                      {cert.data?.course && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          {cert.data.course}
                        </Typography>
                      )}
                      {cert.confidence && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          Confidence: {cert.confidence}%
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Tooltip title="View Certificate">
                  <IconButton 
                    size="small"
                    onClick={() => window.open(url, '_blank')}
                  >
                    <LinkIcon />
                  </IconButton>
                </Tooltip>
              </ListItem>
            ))}
          </List>
          
          {certificates.length > 4 && (
            <Box textAlign="center" mt={1}>
              <Chip
                label={`+${certificates.length - 4} more certificates`}
                size="small"
                color="default"
                variant="outlined"
              />
            </Box>
          )}
        </Box>

        {/* Platform Distribution */}
        <Box mt={2}>
          <Typography variant="subtitle2" mb={1} display="flex" alignItems="center" gap={1}>
            <TrendingIcon sx={{ fontSize: 16 }} />
            Platform Distribution
          </Typography>
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
            {Object.entries(
              certificates.reduce((acc, [, cert]) => {
                const platform = cert.data?.platform || 'Unknown';
                acc[platform] = (acc[platform] || 0) + 1;
                return acc;
              }, {})
            ).map(([platform, count]) => (
              <Chip
                key={platform}
                label={`${platform} (${count})`}
                size="small"
                variant="outlined"
                color="primary"
              />
            ))}
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CertificatesCard; 