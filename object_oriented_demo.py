#!/usr/bin/env python3
"""object_oriented_demo.py

Demonstrates Python's object-oriented programming features:
  - Classes and instances
  - Inheritance and method overriding
  - Encapsulation (private/protected attributes)
  - Class/instance attributes
  - Class methods and static methods
  - Abstract base classes
  - Mixins and multiple inheritance
  - Properties (getters/setters)
  - Polymorphism
"""

from abc import ABC, abstractmethod

class Vehicle(ABC):
    _registry = []

    def __init__(self, name, max_speed):
        self._name = name  # protected attribute
        self.__max_speed = max_speed  # private attribute
        Vehicle._registry.append(self)

    @property
    def name(self):
        """Name of the vehicle."""
        return self._name

    @property
    def max_speed(self):
        """Maximum speed of the vehicle."""
        return self.__max_speed

    @max_speed.setter
    def max_speed(self, speed):
        """Set the max speed with validation."""
        if not Vehicle.is_valid_speed(speed):
            raise ValueError("Speed must be a non-negative number")
        self.__max_speed = speed

    @abstractmethod
    def drive(self):
        """Abstract method to be implemented by subclasses."""
        pass

    @classmethod
    def total_vehicles(cls):
        """Return the total number of vehicles created."""
        return len(cls._registry)

    @staticmethod
    def is_valid_speed(speed):
        """Validate that speed is a non-negative number."""
        return isinstance(speed, (int, float)) and speed >= 0

class Car(Vehicle):
    def __init__(self, name, max_speed, num_doors):
        super().__init__(name, max_speed)
        self.num_doors = num_doors

    def drive(self):
        print(f"{self.name} car is driving at {self.max_speed} km/h with {self.num_doors} doors.")

class Boat(Vehicle):
    def __init__(self, name, max_speed, hull_type):
        super().__init__(name, max_speed)
        self.hull_type = hull_type

    def drive(self):
        print(f"{self.name} boat is sailing at {self.max_speed} knots with a {self.hull_type} hull.")

class FlyableMixin:
    def fly(self):
        print(f"{self.name} is flying at {self.max_speed} km/h.")

class FlyingCar(Car, FlyableMixin):
    def __init__(self, name, max_speed, num_doors):
        super().__init__(name, max_speed, num_doors)

def drive_vehicle(vehicle):
    """Demonstrate polymorphism: different vehicles drive."""
    vehicle.drive()

def main():
    # Create instances
    car = Car("Sedan", 180, 4)
    boat = Boat("Yacht", 40, "fiberglass")
    flying_car = FlyingCar("JetCar", 250, 2)

    # Class method
    print("Total vehicles created:", Vehicle.total_vehicles())

    # Polymorphism
    drive_vehicle(car)
    drive_vehicle(boat)

    print("\nFlyingCar capabilities:")
    drive_vehicle(flying_car)
    flying_car.fly()

    # Property setter and validation
    print("\nTesting property and validation:")
    print("Is 100 a valid speed?", Vehicle.is_valid_speed(100))
    try:
        car.max_speed = -10
    except ValueError as e:
        print("Error:", e)

    # Encapsulation demonstration
    print("\nEncapsulation:")
    try:
        print(car.__max_speed)
    except AttributeError:
        print("Cannot access private attribute __max_speed directly.")

if __name__ == "__main__":
    main()