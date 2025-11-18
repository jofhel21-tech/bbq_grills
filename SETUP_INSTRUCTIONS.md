# BBQ Grill Order Tracking with Map Integration - Setup Instructions

## Overview
This update adds interactive Leaflet maps to the order system, allowing customers to select their delivery location on a map and enabling real-time tracking with both customer and delivery person locations.

## Changes Made

### 1. Database Models Updated (`core/models.py`)

#### Order Model - New Fields:
- `delivery_address` - Full delivery address (TextField)
- `delivery_latitude` - Delivery location latitude (FloatField)
- `delivery_longitude` - Delivery location longitude (FloatField)
- `delivery_barangay` - Barangay/District in Naval (CharField)

#### OrderTracking Model - New Fields:
- `customer_latitude` - Customer location latitude (FloatField)
- `customer_longitude` - Customer location longitude (FloatField)
- `customer_location_name` - Customer location name (CharField)

### 2. Forms Updated (`core/forms.py`)

#### OrderForm - Enhanced with:
- Delivery address textarea
- Barangay/District field
- Hidden latitude/longitude fields (populated by map)

### 3. Templates Updated

#### `templates/core/order_form.html` - New Features:
- Interactive Leaflet map for selecting delivery location
- Click on map to place marker
- Drag marker to adjust location
- Automatic coordinate capture
- Service area circle visualization
- Real-time address and barangay input

#### `templates/core/order_tracking.html` - Enhanced with:
- Dual-marker map showing:
  - Red marker = Customer delivery location
  - Gold marker = Delivery person current location
- Dashed line connecting both locations
- Sidebar cards showing both locations
- Improved map legend

### 4. New Map Features

#### Order Creation/Editing Map:
- Centered on Naval, Biliran (11.5667°N, 124.5667°E)
- Zoom level 15 for street-level detail
- Draggable marker for precise location selection
- Click anywhere to place marker
- Service area circle (5km radius)
- Automatic coordinate capture to hidden fields

#### Order Tracking Map:
- Shows delivery person location (gold marker)
- Shows customer delivery location (red marker)
- Dashed line showing delivery route
- Auto-centered between both locations
- Zoom level 14 for optimal view

## Installation Steps

### Step 1: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the new database fields for delivery locations.

### Step 2: Restart Django Server
```bash
python manage.py runserver
```

### Step 3: Test the Features

#### Test Order Form with Map:
1. Go to Orders page
2. Click "Edit" on any order
3. Scroll down to "Delivery Location" section
4. Click on the map to select delivery location
5. Or drag the red marker to adjust
6. Fill in delivery address and barangay
7. Click "Update Order"

#### Test Order Tracking:
1. Go to Orders page
2. Click "Track" on any order
3. If order is "out_for_delivery", map will show both locations
4. View delivery person and customer locations on the map

## Map Interactions

### Order Form Map:
- **Click on map**: Place marker at clicked location
- **Drag marker**: Adjust delivery location precisely
- **Service area**: Shows 5km delivery radius (gold circle)
- **Coordinates**: Automatically captured and stored

### Order Tracking Map:
- **Red marker**: Your delivery location (from order)
- **Gold marker**: Delivery person's current location
- **Dashed line**: Route from delivery person to you
- **Legend**: Shows marker meanings

## Database Fields Reference

### Order Model
```python
delivery_address = TextField()           # Full address
delivery_latitude = FloatField()         # GPS latitude
delivery_longitude = FloatField()        # GPS longitude
delivery_barangay = CharField(max_length=100)  # Barangay name
```

### OrderTracking Model
```python
# Delivery person location
latitude = FloatField()                  # Current location latitude
longitude = FloatField()                 # Current location longitude
location_name = CharField()              # Current location description

# Customer location
customer_latitude = FloatField()         # Customer location latitude
customer_longitude = FloatField()        # Customer location longitude
customer_location_name = CharField()     # Customer location description
```

## API Integration Notes

### Leaflet Library:
- CDN: `https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/`
- OpenStreetMap tiles used (free, no API key required)
- Color markers from: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/`

### Naval, Biliran Coordinates:
- Latitude: 11.5667°N
- Longitude: 124.5667°E
- Service area radius: 5km

## Troubleshooting

### Map not showing:
- Check browser console for errors
- Ensure Leaflet CDN is accessible
- Verify map container has proper height (400px)

### Coordinates not saving:
- Check that hidden fields are present in form
- Verify form submission includes coordinate data
- Check database migration was applied

### Marker not dragging:
- Ensure `draggable: true` is set in marker options
- Check for JavaScript errors in console

## Future Enhancements

1. Add real-time location updates via WebSocket
2. Implement distance calculation between locations
3. Add estimated delivery time based on distance
4. Integrate with actual delivery person GPS
5. Add route optimization
6. Implement customer notifications on location updates

## Support

For issues or questions, check:
- Browser console for JavaScript errors
- Django logs for backend errors
- Database migration status: `python manage.py showmigrations`
