# Map Features Quick Guide

## 🗺️ Order System Map Integration

### What's New?

Your BBQ Grill order system now includes interactive maps for:
1. **Selecting delivery locations** when creating/editing orders
2. **Real-time tracking** showing both customer and delivery person locations

---

## 📍 Order Form - Delivery Location Selection

### How to Use:

1. **Navigate to Order Edit Page**
   - Go to Orders → Click Edit on any order

2. **Scroll to "Delivery Location" Section**
   - Fill in delivery address (text area)
   - Enter barangay/district name

3. **Use the Interactive Map**
   - **Click anywhere on map** → Places red marker at that location
   - **Drag the red marker** → Adjust location precisely
   - **Service area circle** → Shows 5km delivery radius

4. **Automatic Coordinate Capture**
   - Latitude and longitude are automatically saved
   - No manual coordinate entry needed

5. **Submit the Form**
   - Click "Update Order"
   - Delivery location is saved with coordinates

### Map Features:
- ✅ OpenStreetMap tiles (free, always available)
- ✅ Centered on Naval, Biliran
- ✅ Zoom level 15 (street-level detail)
- ✅ Draggable marker
- ✅ Click-to-place functionality
- ✅ Service area visualization

---

## 🚚 Order Tracking - Live Delivery Map

### How to Use:

1. **Navigate to Order Tracking**
   - Go to Orders → Click Track on any order
   - Map appears if order is "out_for_delivery"

2. **View Both Locations**
   - **Red Marker** = Your delivery location
   - **Gold Marker** = Delivery person's current location
   - **Dashed Line** = Route between them

3. **Understand the Display**
   - Map automatically centers between both locations
   - Zoom level 14 shows both points clearly
   - Sidebar shows detailed location information

### Sidebar Information:
- **Estimated Delivery** - When order should arrive
- **Your Delivery Location** - Address and barangay
- **Delivery Person Location** - Current location name and coordinates

### Map Legend:
```
🔴 Red Marker    = Your Delivery Location
🟡 Gold Marker   = Delivery Person Location
--- Dashed Line  = Route/Connection
```

---

## 🎯 Key Coordinates

### Naval, Biliran
- **Latitude**: 11.5667°N
- **Longitude**: 124.5667°E
- **Service Area**: 5km radius (shown as gold circle)

### Barangays in Naval (Examples)
- Barangay Caraycaray
- Barangay Cabucgayan
- Barangay Bilangbilangan
- Barangay Caibiran
- Barangay Calanipa
- Barangay Calubang
- Barangay Camandag
- Barangay Camuning
- Barangay Canigao
- Barangay Carabalan
- Barangay Carabao
- Barangay Carabutan
- Barangay Carasacan
- Barangay Carasacan
- Barangay Caratagan
- Barangay Caratala
- Barangay Caratula
- Barangay Carauan
- Barangay Caray
- Barangay Caraycaray

---

## 💾 Database Fields

### Order Model
```
delivery_address      → Full delivery address
delivery_latitude     → GPS latitude coordinate
delivery_longitude    → GPS longitude coordinate
delivery_barangay     → Barangay/District name
```

### OrderTracking Model
```
latitude              → Delivery person's latitude
longitude             → Delivery person's longitude
location_name         → Delivery person's location description
customer_latitude     → Customer's delivery location latitude
customer_longitude    → Customer's delivery location longitude
customer_location_name → Customer's location description
```

---

## 🔧 Technical Details

### Technologies Used
- **Leaflet.js** v1.9.4 - Interactive mapping library
- **OpenStreetMap** - Free map tiles
- **Color Markers** - Custom marker colors (red, gold)
- **Django Forms** - Backend form handling

### API Endpoints
- Map tiles: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- Color markers: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/`

### No API Keys Required
- ✅ OpenStreetMap is free
- ✅ No authentication needed
- ✅ No rate limiting for basic usage

---

## ⚡ Quick Tips

### For Customers:
1. Click on map to select exact delivery location
2. Drag marker to fine-tune position
3. Always enter barangay for accurate delivery
4. Check tracking map to see delivery person approaching

### For Staff:
1. Update delivery person location in tracking
2. Monitor both locations on tracking map
3. Use coordinates for GPS navigation
4. Set estimated delivery time for customer

### Best Practices:
- ✅ Always fill in barangay information
- ✅ Use map to select precise location
- ✅ Update delivery person location regularly
- ✅ Verify coordinates before saving

---

## 🐛 Troubleshooting

### Map Not Showing?
- Check internet connection (needs CDN access)
- Clear browser cache
- Try different browser
- Check browser console for errors

### Marker Not Moving?
- Ensure you're clicking on the map
- Try dragging the marker instead
- Refresh the page
- Check JavaScript is enabled

### Coordinates Not Saving?
- Verify form submission completed
- Check database migration ran
- Look for form validation errors
- Check browser console

---

## 📱 Mobile Compatibility

- ✅ Works on mobile browsers
- ✅ Touch-friendly marker dragging
- ✅ Responsive map sizing
- ✅ Optimized for small screens

---

## 🔐 Privacy & Security

- ✅ Coordinates stored in database
- ✅ Only visible to order owner and staff
- ✅ No external tracking
- ✅ No personal data sent to third parties

---

## 📞 Support

For issues:
1. Check browser console (F12)
2. Verify database migrations: `python manage.py showmigrations`
3. Restart Django server
4. Clear browser cache and try again

---

**Last Updated**: November 6, 2025
**Version**: 1.0
