document.addEventListener('DOMContentLoaded', function() {
    const checkButtons = document.querySelectorAll('.availability-check');
    
    checkButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const roomId = this.getAttribute('data-room-id');
            const checkInDate = document.querySelector('[name="check_in_date"]').value;
            const checkOutDate = document.querySelector('[name="check_out_date"]').value;

            if (!checkInDate || !checkOutDate) {
                alert('Please select both check-in and check-out dates.');
                return;
            }

            fetch(`/check-availability/${roomId}/?check_in_date=${checkInDate}&check_out_date=${checkOutDate}`)
                .then(response => response.json())
                .then(data => {
                    if (data.available) {
                        alert('Room is available!');
                    } else {
                        alert('Room is not available for the selected dates.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while checking availability.');
                });
        });
    });
});
