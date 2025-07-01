document.addEventListener('DOMContentLoaded', function() {
    const API_BASE_URL = 'http://localhost:5000';

    
    
    // Form submissions
    document.getElementById('createRideForm').addEventListener('submit', createRide);
    document.getElementById('updateRideForm').addEventListener('submit', updateRideStatus);
    document.getElementById('pricingForm').addEventListener('submit', updatePricing);
    document.getElementById('refreshRides').addEventListener('click', fetchRides);
    document.getElementById('refreshDrivers').addEventListener('click', fetchDrivers);
    
    // Initial data load
    fetchRides();
    fetchDrivers();
    fetchPricingConfigs();
    
    // Create a new ride
    async function createRide(e) {
        e.preventDefault();
        
        const riderId = document.getElementById('riderId').value;
        const pickupLat = document.getElementById('pickupLat').value;
        const pickupLng = document.getElementById('pickupLng').value;
        const dropLat = document.getElementById('dropLat').value;
        const dropLng = document.getElementById('dropLng').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/rides`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rider_id: riderId,
                    pickup_lat: pickupLat,
                    pickup_lng: pickupLng,
                    drop_lat: dropLat,
                    drop_lng: dropLng
                })
            });
            
            if (response.ok) {
                alert('Ride created successfully!');
                fetchRides();
                document.getElementById('createRideForm').reset();
            } else {
                const error = await response.json();
                alert(`Error: ${error.message || 'Failed to create ride'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
    
    // Update ride status
    async function updateRideStatus(e) {
        e.preventDefault();
        
        const rideId = document.getElementById('rideId').value;
        const status = document.getElementById('status').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/rides/${rideId}/update_status`, {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status: status
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            alert('Ride status updated successfully!');
            fetchRides();
            document.getElementById('updateRideForm').reset();
        } catch (error) {
            console.error('Error updating ride status:', error);
            alert(`Error: ${error.message}`);
        }
    }
    
    // Update pricing configuration
    async function updatePricing(e) {
        e.preventDefault();
        
        const key = document.getElementById('configKey').value;
        const value = document.getElementById('configValue').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/pricing`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    key: key,
                    value: value
                })
            });
            
            if (response.ok) {
                alert('Pricing configuration updated successfully!');
                fetchPricingConfigs();
                document.getElementById('pricingForm').reset();
            } else {
                const error = await response.json();
                alert(`Error: ${error.message || 'Failed to update pricing'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
    
    // Fetch all rides
    async function fetchRides() {
        try {
            const response = await fetch(`${API_BASE_URL}/rides`);
            const rides = await response.json();
            
            const ridesList = document.getElementById('ridesList');
            ridesList.innerHTML = '';
            
            if (rides.length === 0) {
                ridesList.innerHTML = '<p>No rides found</p>';
                return;
            }
            
            rides.forEach(ride => {
                const rideItem = document.createElement('div');
                rideItem.className = `ride-item status-${ride.status}`;
                
                rideItem.innerHTML = `
                    <h3>Ride #${ride.id}</h3>
                    <p><strong>Status:</strong> <span class="status-${ride.status}">${ride.status}</span></p>
                    <p><strong>Rider ID:</strong> ${ride.rider_id}</p>
                    <p><strong>Driver ID:</strong> ${ride.driver_id || 'Not assigned'}</p>
                    <p><strong>Pickup:</strong> (${ride.pickup_lat}, ${ride.pickup_lng})</p>
                    <p><strong>Drop:</strong> (${ride.drop_lat}, ${ride.drop_lng})</p>
                    ${ride.fare ? `<p><strong>Fare:</strong> $${ride.fare.toFixed(2)}</p>` : ''}
                    <p><small>Created: ${new Date(ride.created_at).toLocaleString()}</small></p>
                `;
                
                ridesList.appendChild(rideItem);
            });
        } catch (error) {
            console.error('Error fetching rides:', error);
        }
    }
    
    // Fetch all drivers
    async function fetchDrivers() {
        try {
            const response = await fetch(`${API_BASE_URL}/drivers`);
            const drivers = await response.json();
            
            const driversList = document.getElementById('driversList');
            driversList.innerHTML = '';
            
            if (drivers.length === 0) {
                driversList.innerHTML = '<p>No drivers found</p>';
                return;
            }
            
            drivers.forEach(driver => {
                const driverItem = document.createElement('div');
                driverItem.className = `driver-item driver-${driver.is_available ? 'available' : 'unavailable'}`;

                let statusText = '';
                if (driver.status === 'available') {
                    statusText = 'Available';
                } else if (driver.status === 'in_ride') {
                    statusText = 'On a Ride';
                } else {
                    statusText = 'Offline';
                }
                
                driverItem.innerHTML = `
                    <h3>Driver #${driver.id}: ${driver.name}</h3>
                    <p><strong>Status:</strong> ${statusText}</p>
                    <p><strong>Location:</strong> (${driver.current_lat}, ${driver.current_lng})</p>
                    <p><strong>Cancel Count:</strong> ${driver.cancel_count}</p>
                `;

                
                
                driversList.appendChild(driverItem);
            });
        } catch (error) {
            console.error('Error fetching drivers:', error);
        }
    }
    
    // Fetch pricing configurations
    async function fetchPricingConfigs() {
        try {
            const response = await fetch(`${API_BASE_URL}/pricing`);
            const configs = await response.json();
            
            const pricingList = document.getElementById('pricingList');
            pricingList.innerHTML = '';
            
            if (configs.length === 0) {
                pricingList.innerHTML = '<p>No pricing configurations found</p>';
                return;
            }
            
            configs.forEach(config => {
                const configItem = document.createElement('div');
                configItem.className = 'pricing-item';
                
                configItem.innerHTML = `
                    <p><strong>${config.key}:</strong> $${config.value}</p>
                `;
                
                pricingList.appendChild(configItem);
            });
        } catch (error) {
            console.error('Error fetching pricing configurations:', error);
        }
    }
});