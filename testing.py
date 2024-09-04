import matplotlib.pyplot as plt
import os



student_scores = {
    '2021': [75, 78, 80, 82, 85, 88, 90, 92, 95],
    '2022': [65, 68, 70, 72, 75, 78, 80, 82, 85],
    '2023': [85, 88, 90, 92, 95, 98, 100, 102, 105],
    '2024': [60, 62, 65, 67, 70, 72, 75, 78, 80]
}
def create_student_scores_plot(student_scores, output_dir='static/images'):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # X-axis labels

    terms = ['Term 1 Exam 1', 'Term 1 Exam 2', 'Term 1 Exam 3',
             'Term 2 Exam 1', 'Term 2 Exam 2', 'Term 2 Exam 3',
             'Term 3 Exam 1', 'Term 3 Exam 2', 'Term 3 Exam 3']

    # Plot each year's data with a different color
    plt.figure(figsize=(10, 6))
    for year, scores in student_scores.items():
        plt.plot(terms, scores, label=f'Year {year}')

    # Add title and labels
    plt.title('Student Scores Over the Years')
    plt.xlabel('Examinations')
    plt.ylabel('Scores')
    plt.legend(title='Year')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.grid(True)

    # Save the plot as a PNG file
    plot_path = os.path.join(output_dir, 'student_scores.png')
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()  # Close the plot to free up memory

    return plot_path
