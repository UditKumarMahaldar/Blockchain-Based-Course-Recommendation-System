// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CourseRecommendation {
    struct Course {
        string courseName;
        string difficultyLevel;
        string courseDescription;
        string skills;
    }

    Course[] public courses;

    function addCourse(
        string memory _courseName,
        string memory _difficultyLevel,
        string memory _courseDescription,
        string memory _skills
    ) public {
        courses.push(
            Course({
                courseName: _courseName,
                difficultyLevel: _difficultyLevel,
                courseDescription: _courseDescription,
                skills: _skills
            })
        );
    }

    function getCourseCount() public view returns (uint256) {
        return courses.length;
    }

    function getCourse(uint256 index)
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        Course memory course = courses[index];
        return (
            course.courseName,
            course.difficultyLevel,
            course.courseDescription,
            course.skills
        );
    }
}