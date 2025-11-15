# MatchColab Frontend

A modern, responsive web interface for the MatchColab Artist Collaboration Matchmaker.

## Features

- **Real-time Health Monitoring**: Minimal status indicator (footer) with accessibility text
- **Artist Matching**: Find compatible artists based on your music style tags
- **Optional Success Filter**: Toggle to restrict matches to artists with successful collaboration history
- **Fixed Parameters**: Always returns top 10 matches with minimum similarity fixed at 0.5 (not user adjustable)
- **Artist Profile Persistence**: Save your artist profile to the database for future matches
- **Beautiful UI**: Modern dark theme with smooth animations and responsive design

## Files

- `index.html` - Main HTML structure
- `styles.css` - Responsive CSS styling with dark theme
- `app.js` - Frontend JavaScript for API integration

## Usage

### Local Development

1. Start the backend server:
```bash
cd backend
npm install
npm run dev
```

2. Open your browser to `http://localhost:5000`

The frontend is automatically served by the backend Express server.

### API Integration

The frontend connects to the following endpoints:

- `GET /health` - Health check and system status
- `POST /match` - Find artist matches

### Example Request

When you submit the form with tags "pop, r&b", the frontend sends:

```json
{
  "tags": "pop, r&b",
  "top_n": 10,
  "min_similarity": 0.5,
  "only_successful": false,
  "artist_name": null,
  "persist_artist": false
}
```

### Response Format (Simplified)

The API now returns only the blended overall score (component scores removed):

```json
{
  "user_tags": "pop, r&b",
  "parameters": {
    "top_n": 10,
    "only_successful": false,
    "min_similarity": 0.5
  },
  "matches": [
    {
      "artist_name": "Ariana Grande",
      "artist_tags": "contemporary r&b, dance-pop, pop, r&b",
      "overall_score": 0.797,
      "recommendation": "HIGHLY RECOMMENDED - Strong compatibility!"
    }
  ],
  "total_matches": 10
}
```

## Customization

### Changing API URL

By default, the frontend auto-detects the API URL:
- `localhost` → `http://localhost:5000`
- Other domains → Same origin

To change this, edit `app.js`:

```javascript
const API_BASE_URL = 'https://your-api-url.com';
```

### Styling

All colors and styles are defined in `styles.css` using CSS variables:

```css
:root {
    --primary-color: #6366f1;
    --success-color: #10b981;
    /* ... more variables */
}
```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Production Deployment

When deploying to production:

1. Set the `CORS_ORIGIN` environment variable on your backend to allow your frontend domain
2. Ensure HTTPS is enabled
3. Consider serving frontend from a CDN for better performance

## Troubleshooting

**Health check shows "degraded"**
- Check that Supabase credentials are configured in backend `.env`
- Verify OpenAI API key is set

**"Cannot connect to server" error**
- Ensure backend server is running on port 5000
- Check browser console for CORS errors

**No matches found**
- Try lowering the minimum similarity threshold
- Verify artists are in the database with embeddings
- Check that tags are comma-separated

## License

MIT
