'''
    database access
'''
            
            
            
            booking = Booking()
            booking.requestSpecialty = self.request.get('categories')
            booking.put()