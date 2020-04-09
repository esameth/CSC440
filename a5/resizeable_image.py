import imagematrix
import numpy as np

class ResizeableImage(imagematrix.ImageMatrix):
    """
    Calculates and returns the best path from each column in the last row and their energies
    """
    def DFS(self, energy_map, col, row):
        # Base case -if we've reached row 0
        if row == 0:
            return [(col, row)], self.energy(col, row)

         # We are in the first column
        if col == 0:
            # Get the upper right and the one above
            path1, energy1 = self.DFS(energy_map, col + 1, row - 1)
            path2, energy2 = self.DFS(energy_map, col, row - 1)

            # Check which one has a lower energy
            energies = min(energy1, energy2)
            path = path1
            if energies == energy2:
                path = path2

        # We are in the last column
        elif col == self.width - 1:
            # Get the one above and the one on the upper left
            path1, energy1 = self.DFS(energy_map, col, row - 1)
            path2, energy2 = self.DFS(energy_map, col - 1, row - 1)

            # Check which one has a lower energy
            energies = min(energy1, energy2)
            path = path1
            if energies == energy2:
                path = path2

        else:
            # Get the one to the upper left, the one above, and the one to the upper right
            path1, energy1 = self.DFS(energy_map, col - 1, row - 1)
            path2, energy2 = self.DFS(energy_map, col, row - 1)
            path3, energy3 = self.DFS(energy_map, col + 1, row - 1)

            # Check which one has a lower energy
            energies = min(energy1, energy2, energy3)
            path = path1
            if energies == energy2:
                path = path2
            elif energies == energy3:
                path = path3

        # Add to the total energy
        energies += energy_map[col][row]
        # Add to the path
        path.append((col, row))

        return path, energies


    def best_seam(self, dp=True):
        """
        naive:
            given an image, we are trying to compute every seam
            one of the invariants: if a pixel is at row i, col j -the seam pixel at i+1 --> j - 1, j, j+1
            w distinct ternary tree  -the fact that they overlap is irrelevant
            depth-first traversal (Recursively) -not complete so need to handle special case if at an edge
            return a collection of (path, energy) and find the best one
        """
        if dp == False:
            # Create an energy map that's filled with all 0s -it has the same dimensions as the image
            energy_map = np.zeros(shape=(self.height, self.width), dtype=np.int32)

            # Will hold the paths from DFS
            allPaths = []

            # Fill the energy map with their values
            for j in range(self.height):
                for i in range(self.width):
                    energy_map[i][j] = self.energy(i, j)

            # Go through the last row and get the best path from each (i, self.height - 1)
            # This calls DFS, a recursive function, to find the best paths
            # It returns a ([path], energy) which is stored into one final list
            for i in range(self.width):
                path, energy = self.DFS(energy_map, i, self.height - 1)
                allPaths[energy] = path

            # Get the minimum energy 
            min_energy = min(allPaths.keys())

            # Get just the path
            finalPath = allPaths[min_energy]

        # Memoization
        else:

            """
            dynamic:
                some data structure to hold cummulative energies -dictionary
                fill in energy values for the first row -just calls to energy function
                    second row -cummulative energy, best energy from some of the pixels above it
            """
            # Holds all of the energies
            energy_map = {}
            # Holds the paths
            path = {}
            # Get the energy of every pixel in the top row
            for i in range(self.width):
                # Key is the tuple (i, 0) and its value is the energy
                energy_map[i, 0] = self.energy(i, 0)

            # Don't start at 0 because we have already looked at the first row
            for j in range(1, self.height):
                for i in range(self.width):
                    position = (i, j - 1)

                    # Checks the upper left and upper right and sees if they are lower than the base, the one above
                    # If it is, reset the position that holds the minimum energy
                    if (i - 1, j - 1) in energy_map.keys() and energy_map[i - 1, j - 1] < energy_map[position]:
                        position = (i - 1, j - 1)

                    if (i + 1, j - 1) in energy_map.keys() and energy_map[i + 1, j - 1] < energy_map[position]:
                        position = (i + 1, j - 1)

                    # The energy of i, j is the energy of itself and the minimum energy calculated above
                    energy_map[i, j] = self.energy(i, j) + energy_map[position]

                    # The path contains as its key, the tuple of the pixel we are looking at (i, j)
                    # and as its value, the position (i, j - 1), (i - 1, j - 1) or (i + 1, j - 1) that was the min
                    path[i, j] = position

            # Start looking at the lower left corner - we will be checking each value in this row to find the min
            # This can be done since the last row contains the added final energies of each path
            minimum = energy_map[0, self.height - 1]
            minPixel = (0, self.height - 1)
            for i in range(1, self.width):
                if energy_map[i, self.height - 1] < minimum:
                    minPixel = (i, self.height - 1)

            # Now that we have which column has the least energy, we have to find its path by traversing the path dict
            finalPath = [minPixel]
            while minPixel in path.keys():
                # Reset the current pixel
                minPixel = path[minPixel]
                # Add it to the final path list
                finalPath.append(minPixel)

        # Return one list of tuples -the seam to remove
        return finalPath

    def remove_best_seam(self):
        self.remove_seam(self.best_seam())
