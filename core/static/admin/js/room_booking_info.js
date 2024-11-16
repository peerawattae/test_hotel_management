function fetchBookingInfo(roomId) {
    // You may need to adjust this if you're using a different route or logic
    fetch(`/admin/room-booking-info/${roomId}/`)  // Custom view route in Django
        .then(response => response.json())
        .then(data => {
            if (data.bookings && data.bookings.length > 0) {
                // If there are bookings, show them in an alert or any other UI element
                alert(
                    `Bookings for Room ${roomId}:\n` +
                    data.bookings.map(b => `${b.check_in_date} to ${b.check_out_date}`).join("\n")
                );
            } else {
                alert(`No bookings found for Room ${roomId}.`);
            }
        })
        .catch(error => console.error('Error fetching booking info:', error));
}
